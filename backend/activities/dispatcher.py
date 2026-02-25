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
    Dispatch a workflow step to the correct typed activity.

    This activity:
        1. Fetches the component from the database by component_id.
        2. Determines the component category.
        3. Delegates to the matching handler from COMPONENT_REGISTRY.
        4. Returns the handler's structured result.

    Args:
        input: Dict containing:
            - component_id (str): UUID of the component to execute.
            - inputs (dict): Input parameters for the component.
            - step_id (str): ID of the workflow step.

    Returns:
        Structured result from the delegated handler.

    Raises:
        ValueError: If component is not found or category is unsupported.
    """
    component_id: str = input["component_id"]
    step_inputs: Dict[str, Any] = input.get("inputs", {})
    step_id: str = input.get("step_id", "unknown")

    logger.info(
        "Dispatching component step — step_id=%s component_id=%s",
        step_id,
        component_id,
    )

    # ------------------------------------------------------------------
    # 1. Fetch component from DB
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # 2. Determine the category to route on
    # ------------------------------------------------------------------
    category = (component.category or "").strip().lower()

    # Fallback: if category is empty, try to infer from component name
    if not category:
        name_lower = (component.name or "").lower()
        if "notification" in name_lower or "email" in name_lower:
            category = "notification"
        elif "plumber" in name_lower:
            category = "external_plumber"
        elif "contractor" in name_lower:
            category = "external_contractor"
        elif "document" in name_lower or "report" in name_lower:
            category = "document"
        elif "issue" in name_lower or "update" in name_lower:
            category = "issue_update"
        else:
            category = "unknown"

        logger.warning(
            "Component '%s' has no category — inferred '%s' from name '%s'",
            component_id,
            category,
            component.name,
        )

    # ------------------------------------------------------------------
    # 3. Look up the handler
    # ------------------------------------------------------------------
    handler = COMPONENT_REGISTRY.get(category)
    if handler is None:
        raise ValueError(
            f"Unsupported component category '{category}' "
            f"for component '{component_id}' (name='{component.name}'). "
            f"Supported categories: {list(COMPONENT_REGISTRY.keys())}"
        )

    # ------------------------------------------------------------------
    # 4. Merge step context into inputs and delegate
    # ------------------------------------------------------------------
    merged_inputs = {
        **step_inputs,
        "step_id": step_id,
        "component_id": component_id,
        "component_name": component.name,
        "endpoint_url": component.endpoint_url,
    }

    logger.info(
        "Routing step_id=%s to handler=%s (category=%s)",
        step_id,
        handler.__name__,
        category,
    )

    # Call the handler directly (it's an async function, not a Temporal activity call)
    result = await handler(merged_inputs)

    return result
