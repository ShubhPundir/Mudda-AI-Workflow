"""
LLM-based activities for Mudda.
"""
import logging
from temporalio import activity
from sessions.llm import LLMFactory
from schemas.activity_schemas import (
    LLMGenerateDispatchTextInput,
    LLMGenerateDispatchTextOutput,
    GenerateLLMContentInput,
    GenerateLLMContentOutput,
)

logger = logging.getLogger(__name__)
_llm_service = LLMFactory.get_llm_service()

@activity.defn
async def llm_generate_dispatch_text_activity(input: LLMGenerateDispatchTextInput) -> LLMGenerateDispatchTextOutput:
    """Generates instructions or dispatch text for a service."""
    logger.info("Generating dispatch text via LLM")
    
    # In a real implementation, this would call the LLM service with a specific prompt
    prompt = f"Generate dispatch instructions for a {input.category} emergency: {input.description}"
    result = await _llm_service.generate_report({"problem_statement": prompt})
    
    return LLMGenerateDispatchTextOutput(
        dispatch_text=result,
        status="success"
    )

# TODO: refactor later into a simpler single method

@activity.defn
async def generate_llm_content(input: GenerateLLMContentInput) -> GenerateLLMContentOutput:
    """Generates content for a PDF report."""
    logger.info("Generating content for report via LLM")
    result = await _llm_service.generate_report(input.model_dump())
    
    return GenerateLLMContentOutput(
        content=result,
        status="success"
    )
