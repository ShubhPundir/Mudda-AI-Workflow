"""
External service activities for contacting plumber and contractor services.

Uses PlumberAPIAdapter and ContractorAPIAdapter from the infrastructure layer.
"""
import logging
from typing import Any, Dict
from temporalio import activity

from infrastructure.plumber_api_adapter import PlumberAPIAdapter
from infrastructure.contractor_api_adapter import ContractorAPIAdapter

logger = logging.getLogger(__name__)

# Module-level adapter instances
_plumber_adapter = PlumberAPIAdapter()
_contractor_adapter = ContractorAPIAdapter()


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

    result = await _plumber_adapter.contact(input)

    return {
        "step_id": step_id,
        "service": "plumber",
        "result": result,
        "status": "completed",
    }


@activity.defn
async def contact_contractor(input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Contact the contractor external service.

    Args:
        input: Dict containing project details, scope, budget, etc.
            - step_id (str, optional): Originating workflow step ID.
            - issue_id (str, optional): Related civic issue ID.
            - scope (str, optional): Work scope description.
            - budget (float, optional): Estimated budget.
            - timeline (str, optional): Expected timeline.

    Returns:
        Structured JSON with service response.
    """
    step_id = input.get("step_id", "unknown")
    logger.info("contact_contractor activity — step_id=%s", step_id)

    result = await _contractor_adapter.contact(input)

    return {
        "step_id": step_id,
        "service": "contractor",
        "result": result,
        "status": "completed",
    }
