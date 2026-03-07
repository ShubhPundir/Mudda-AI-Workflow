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

# TODO: make human signals