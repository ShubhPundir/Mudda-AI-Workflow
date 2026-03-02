"""
External service activities for contacting plumber and 
contractor (deprecated) --> Next patch should include an inheritance structure for external activity

services.
Uses PlumberAPIAdapter from the infrastructure layer.
"""
import logging
from temporalio import activity
from infrastructure.plumber.plumber_factory import PlumberFactory
from sessions.llm import LLMFactory
from schemas.activity_schemas import (
    ContactPlumberInput,
    ContactPlumberOutput,
    AwaitPlumberConfirmationInput,
    AwaitPlumberConfirmationOutput,
)

logger = logging.getLogger(__name__)

# Module-level adapter instances
_plumber_service = PlumberFactory.get_plumber_service()
_llm_service = LLMFactory.get_llm_service()


@activity.defn
async def contact_plumber(input: ContactPlumberInput) -> ContactPlumberOutput:
    """
    Contact the plumber external service with LLM-enhanced dispatch instructions.

    LLM service is available for generating contextualized dispatch text if needed.

    Args:
        input: ContactPlumberInput containing issue details, location, urgency, etc.

    Returns:
        ContactPlumberOutput with service response.
    """
    logger.info("contact_plumber activity — step_id=%s", input.step_id)

    # Generate enhanced dispatch text using LLM if description is provided
    enhanced_input = input.model_dump()
    if input.description:
        prompt = f"Generate dispatch instructions for a {input.urgency} urgency plumbing issue: {input.description}"
        if input.location:
            prompt += f" at location: {input.location}"
        
        logger.info("Generating LLM-enhanced dispatch text")
        dispatch_text = await _llm_service.generate_report({"problem_statement": prompt})
        enhanced_input["dispatch_text"] = dispatch_text

    result = await _plumber_service.contact(enhanced_input)

    return ContactPlumberOutput(
        step_id=input.step_id,
        service="plumber",
        result=result,
        status="completed",
    )


@activity.defn
async def await_plumber_confirmation_activity(input: AwaitPlumberConfirmationInput) -> AwaitPlumberConfirmationOutput:
    """
    Logs that a follow-up is expected from the plumber with LLM-generated follow-up instructions.
    """
    logger.info("await_plumber_confirmation_activity: follow-up expected")

    # Generate intelligent follow-up message using LLM
    prompt = f"Generate follow-up instructions for plumber confirmation based on: {input.model_dump()}"
    logger.info("Generating LLM-enhanced follow-up instructions")
    follow_up_instructions = await _llm_service.generate_report({"problem_statement": prompt})

    # TODO: Implement actual waiting mechanism (e.g., polling, signal) in Backend

    # Simulation: Log to DB or system that we are waiting for a signal
    return AwaitPlumberConfirmationOutput(
        status="waiting_for_signal",
        message=f"System is now expecting a follow-up signal from plumber. Instructions: {follow_up_instructions[:100]}..."
    )
