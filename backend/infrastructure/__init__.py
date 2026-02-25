"""
Infrastructure adapter layer for Mudda AI Workflow system.

Thin wrappers around external integrations (email, APIs, PDF, LLM).
No Temporal decorators — these are plain async classes.
"""
from .email_adapter import EmailAdapter
from .plumber_api_adapter import PlumberAPIAdapter
from .contractor_api_adapter import ContractorAPIAdapter
from .pdf_generator import PDFGenerator
from .llm_service import LLMService

__all__ = [
    "EmailAdapter",
    "PlumberAPIAdapter",
    "ContractorAPIAdapter",
    "PDFGenerator",
    "LLMService",
]
