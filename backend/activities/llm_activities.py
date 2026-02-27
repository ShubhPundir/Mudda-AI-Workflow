"""
LLM-based activities for Mudda.
"""
import logging
from typing import Any, Dict
from temporalio import activity
from sessions.llm import LLMFactory

logger = logging.getLogger(__name__)
_llm_service = LLMFactory.get_llm_service()

@activity.defn
async def llm_generate_dispatch_text_activity(input: Dict[str, Any]) -> Dict[str, Any]:
    """Generates instructions or dispatch text for a service."""
    logger.info("Generating dispatch text via LLM")
    description = input.get("description", "No description provided")
    category = input.get("category", "General")
    
    # In a real implementation, this would call the LLM service with a specific prompt
    prompt = f"Generate dispatch instructions for a {category} emergency: {description}"
    result = await _llm_service.generate_report({"problem_statement": prompt})
    
    return {
        "dispatch_text": result,
        "status": "success"
    }

# TODO: refactor later into a simpler single method

@activity.defn
async def generate_llm_content(input: Dict[str, Any]) -> Dict[str, Any]:
    """Generates content for a PDF report."""
    logger.info("Generating content for report via LLM")
    result = await _llm_service.generate_report(input)
    
    return {
        "content": result,
        "status": "success"
    }
