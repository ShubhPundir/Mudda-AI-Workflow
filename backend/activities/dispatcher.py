"""
Dispatcher activity — the central routing hub for component step execution.

Provides dynamic orchestration of activities defined in the database.
Handles retries, configuration merging, and sequential data flow.
"""
import asyncio
import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional

from temporalio import activity
from temporalio.common import RetryPolicy

# Import all activities to populate the registry
from activities import (
    send_notification,
    contact_plumber,
    contact_contractor,
    await_plumber_confirmation_activity,
    generate_report,
    pdf_service_activity,
    update_issue,
    llm_generate_dispatch_text_activity,
    generate_llm_content,
    human_feedback_activity,
    human_verification_activity,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Component Registry
# Maps activity names (string) to the actual activity function.
# ---------------------------------------------------------------------------
COMPONENT_REGISTRY: Dict[str, Any] = {
    "send_notification": send_notification,
    "contact_plumber": contact_plumber,
    "contact_contractor": contact_contractor,
    "await_plumber_confirmation_activity": await_plumber_confirmation_activity,
    "generate_report": generate_report,
    "pdf_service_activity": pdf_service_activity,
    "update_issue": update_issue,
    "llm_generate_dispatch_text_activity": llm_generate_dispatch_text_activity,
    "generate_llm_content": generate_llm_content,
    "human_feedback_activity": human_feedback_activity,
    "human_verification_activity": human_verification_activity,
}


async def execute_with_retry(
    handler: Any, 
    inputs: Dict[str, Any], 
    retry_config: Optional[Dict[str, Any]] = None
) -> Any:
    """
    Executes an activity handler with a local retry mechanism.
    
    In a full Temporal setup, these would be separate activity calls from the workflow,
    but here we orchestrate them inside the dispatcher as requested.
    """
    if not retry_config:
        retry_config = {}

    max_attempts = retry_config.get("maximum_attempts", 3)
    initial_interval = retry_config.get("initial_interval", 1)
    backoff_coeff = retry_config.get("backoff_coefficient", 2.0)
    
    last_exception = None
    current_interval = initial_interval

    for attempt in range(1, max_attempts + 1):
        try:
            return await handler(inputs)
        except Exception as e:
            last_exception = e
            logger.warning(
                "Activity attempt %d failed: %s. Retrying in %ds...", 
                attempt, str(e), current_interval
            )
            if attempt < max_attempts:
                await asyncio.sleep(current_interval)
                current_interval *= backoff_coeff
            else:
                logger.error("Activity failed after %d attempts", max_attempts)
                raise last_exception


@activity.defn
async def dispatch_component_step(input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dispatch a workflow step to a business component.
    The component orchestrates its internal activities defined in the DB.
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
    results = {}
    # cumulative_inputs starts with step_inputs and grows as activities return data
    cumulative_inputs = {**step_inputs}
    
    component_activities = component.activities or []
    
    for act_config in component_activities:
        activity_name = act_config.get("activity_name")
        if not activity_name:
            continue
            
        logger.info("Running internal activity: %s for component: %s", activity_name, component.name)
        
        handler = COMPONENT_REGISTRY.get(activity_name)
        if not handler:
            logger.warning("No handler found for activity: %s", activity_name)
            continue

        # Prepare activity inputs
        # Merge cumulative inputs, activity metadata, and component config
        activity_inputs = {
            **cumulative_inputs,
            "metadata": act_config.get("metadata", {}),
            "config": component.config,
            "step_id": step_id,
            "component_id": str(component.id),
            "component_name": component.name
        }

        # Execute activity with local retry policy from DB
        try:
            retry_policy = act_config.get("retry_policy", {})
            act_result = await execute_with_retry(handler, activity_inputs, retry_policy)
            
            results[activity_name] = act_result
            
            # Update cumulative inputs for next activity (Sequential Data Flow)
            if isinstance(act_result, dict):
                cumulative_inputs.update(act_result)
            
        except Exception as e:
            logger.error("Component %s halted: Activity %s failed: %s", component.name, activity_name, str(e))
            results[activity_name] = {"success": False, "error": str(e)}
            # Halt component execution on any activity failure after retries
            raise

    return {
        "status": "completed",
        "step_id": step_id,
        "component_id": str(component.id),
        "results": results,
        "cumulative_outputs": cumulative_inputs # Final state of inputs/outputs
    }
