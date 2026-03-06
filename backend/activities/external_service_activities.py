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

# TODO: make plumber dispatch workflow activity defn