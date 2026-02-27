"""
External service activities for contacting plumber and 
contractor (deprecated) --> Next patch should include an inheritance structure for external activity

services.
Uses PlumberAPIAdapter from the infrastructure layer.
"""
import logging
from typing import Any, Dict
from temporalio import activity

logger = logging.getLogger(__name__)

# Module-level adapter instances
_plumber_service = PlumberFactory.get_plumber_service()


@activity.defn
async def contact_plumber(input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Contact the plumber external service.

    Args:
        input: Dict containing issue details, location, urgency, etc.
            - step_id (str, optional): Originating workflow step ID.
            - issue_id (str, optional): Related civic issue ID.
            - location (str, optional): Service location.
            - description (str, optional): Problem description.
            - urgency (str, optional): 'low', 'medium', 'high', 'critical'.

    Returns:
        Structured JSON with service response.
    """
    step_id = input.get("step_id", "unknown")
    logger.info("contact_plumber activity — step_id=%s", step_id)

    result = await _plumber_service.contact(input)

    return {
        "step_id": step_id,
        "service": "plumber",
        "result": result,
        "status": "completed",
    }


@activity.defn
async def await_plumber_confirmation_activity(input: Dict[str, Any]) -> Dict[str, Any]:
    """Logs that a follow-up is expected from the plumber."""
    logger.info("await_plumber_confirmation_activity: follow-up expected")

    # TODO: Implement actual waiting mechanism (e.g., polling, signal) in Backend

    # Simulation: Log to DB or system that we are waiting for a signal
    return {
        "status": "waiting_for_signal",
        "message": "System is now expecting a follow-up signal from plumber"
    }
