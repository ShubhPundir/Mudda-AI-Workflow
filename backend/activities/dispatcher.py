"""
Dispatcher activity — the central routing hub for component step execution.

Replaces the old monolithic execute_component_step.
Fetches the component from DB, inspects its category, and delegates
to the appropriate typed activity function.
"""
import logging
from typing import Any, Dict
from temporalio import activity

from activities.notification_activities import send_notification
from activities.external_service_activities import contact_plumber, contact_contractor
from activities.document_activities import generate_report
from activities.issue_activities import update_issue

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Component Registry
# Maps component category strings to the handler activity function.
# ---------------------------------------------------------------------------
COMPONENT_REGISTRY: Dict[str, Any] = {
    "notification": send_notification,
    "external_plumber": contact_plumber,
    "external_contractor": contact_contractor,
    "document": generate_report,
    "issue_update": update_issue,
}


@activity.defn
async def dispatch_component_step(input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dispatch a workflow step to a business component.
    The component orchestrates its internal activities.

    Args:
        input: Dict containing:
            - component_id (str): UUID of the component to execute.
            - inputs (dict): Input parameters for the component.
            - step_id (str): ID of the workflow step.

    Returns:
        Aggregated results from all internal activities.
    """
    component_id: str = input["component_id"]
    step_inputs: Dict[str, Any] = input.get("inputs", {})
    step_id: str = input.get("step_id", "unknown")

    logger.info(
        "Dispatching component step — step_id=%s component_id=%s",
        step_id,
        component_id,
    )

    # 1. Fetch component from DB
    from sessions.database import AsyncSessionLocal
    from models import Component
    from sqlalchemy.future import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Component).where(Component.id == component_id)
        )
        component = result.scalars().first()

    if component is None:
        raise ValueError(f"Component '{component_id}' not found in database")

    # 2. Iterate and execute internal activities
    # Note: In a full production Temporal setup, these might be called
    # as separate activities via the workflow, but the user requested
    # "Component orchestrates its internal activities".
    
    results = {}
    component_activities = component.activities or []
    
    for act_config in component_activities:
        activity_name = act_config.get("activity_name")
        if not activity_name:
            continue
            
        logger.info("Running internal activity: %s for component: %s", activity_name, component.name)
        
        # Determine the handler from the registry
        handler = COMPONENT_REGISTRY.get(activity_name)
        if not handler:
            # Fallback to category-based lookup if direct name doesn't match
            handler = COMPONENT_REGISTRY.get(component.category.lower() if component.category else "unknown")
            
        if not handler:
            logger.warning("No handler found for activity: %s", activity_name)
            continue

        # Prepare activity inputs
        # Merge global component config, activity metadata, and step inputs
        activity_inputs = {
            **step_inputs,
            "metadata": act_config.get("metadata", {}),
            "config": component.config,
            "step_id": step_id,
            "component_id": str(component.id),
            "component_name": component.name
        }

        # Execute activity (async call within current activity)
        try:
            act_result = await handler(activity_inputs)
            results[activity_name] = act_result
            
            # Update cumulative inputs for next activity if needed
            # (Optional: depends on if we want sequential data flow)
            step_inputs.update(act_result if isinstance(act_result, dict) else {})
            
        except Exception as e:
            logger.error("Activity %s failed: %s", activity_name, str(e))
            results[activity_name] = {"success": False, "error": str(e)}
            # Decide if failure should stop the chain
            # For now, we continue or raise? Let's raise to trigger Temporal retry.
            raise

    return {
        "status": "completed",
        "step_id": step_id,
        "component_id": str(component.id),
        "results": results
    }
