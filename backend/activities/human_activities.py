"""
Activities involving human interaction.
LLM-powered for intelligent prompt generation and response processing.
"""
import logging
from temporalio import activity
from sessions.llm import LLMFactory
from schemas.activity_schemas import (
    HumanFeedbackInput,
    HumanFeedbackOutput,
    HumanVerificationInput,
    HumanVerificationOutput,
)

logger = logging.getLogger(__name__)
_llm_service = LLMFactory.get_llm_service()

@activity.defn
async def human_feedback_activity(input: HumanFeedbackInput) -> HumanFeedbackOutput:
    """
    Request human feedback with LLM-generated contextual prompts.
    In production, this might wait for a signal or interact with a UI.
    """
    logger.info("Waiting for human feedback... (simulated)")

    # Generate intelligent prompt for human using LLM
    prompt = f"Generate a clear, concise prompt for human approval based on: {input.model_dump()}"
    logger.info("Generating LLM-enhanced human feedback prompt")
    human_prompt = await _llm_service.generate_report({"problem_statement": prompt})
    
    # TODO: implement actual human feedback --> connectivity with backend
    
    # TODO: in the later versions, all activities must come with a target to send to

    # The human_prompt would be shown to the user in the UI
    
    # Simulate response with LLM-enhanced feedback
    return HumanFeedbackOutput(
        approved=True,
        feedback=f"Approved by official. Context: {human_prompt[:100]}...",
        status="completed"
    )

@activity.defn
async def human_verification_activity(input: HumanVerificationInput) -> HumanVerificationOutput:
    """
    Verification of external service response by a human with LLM-assisted analysis.
    """
    logger.info("Human verifying external response...")

    # Use LLM to analyze the work and prepare verification checklist
    prompt = f"Analyze this work completion data and generate verification checklist: {input.model_dump()}"
    logger.info("Generating LLM-powered verification checklist")
    verification_checklist = await _llm_service.generate_report({"problem_statement": prompt})
    
    # TODO: implement actual human verification --> connectivity with backend
    # The verification_checklist would be shown to the verifier
    
    return HumanVerificationOutput(
        verified=True,
        notes=f"Work quality verified. Checklist: {verification_checklist[:100]}...",
        status="completed"
    )
