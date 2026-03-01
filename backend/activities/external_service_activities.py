"""
External service activities for contacting plumber and 
contractor (deprecated) --> Next patch should include an inheritance structure for external activity

services.
Uses PlumberAPIAdapter from the infrastructure layer.
"""
import logging
from temporalio import activity
from infrastructure.plumber.plumber_factory import PlumberFactory
from schemas.activity_schemas import (
    ContactPlumberInput,
    ContactPlumberOutput,
    AwaitPlumberConfirmationInput,
    AwaitPlumberConfirmationOutput,
)

logger = logging.getLogger(__name__)

# Module-level adapter instances
_plumber_service = PlumberFactory.get_plumber_service()


@activity.defn
async def contact_plumber(input: ContactPlumberInput) -> ContactPlumberOutput:
    """
    Contact the plumber external service.

    Args:
        input: ContactPlumberInput containing issue details, location, urgency, etc.

    Returns:
        ContactPlumberOutput with service response.
    """
    logger.info("contact_plumber activity — step_id=%s", input.step_id)

    result = await _plumber_service.contact(input.model_dump())

    return ContactPlumberOutput(
        step_id=input.step_id,
        service="plumber",
        result=result,
        status="completed",
    )


@activity.defn
async def await_plumber_confirmation_activity(input: AwaitPlumberConfirmationInput) -> AwaitPlumberConfirmationOutput:
    """Logs that a follow-up is expected from the plumber."""
    logger.info("await_plumber_confirmation_activity: follow-up expected")

    # TODO: Implement actual waiting mechanism (e.g., polling, signal) in Backend

    # Simulation: Log to DB or system that we are waiting for a signal
    return AwaitPlumberConfirmationOutput(
        status="waiting_for_signal",
        message="System is now expecting a follow-up signal from plumber"
    )
