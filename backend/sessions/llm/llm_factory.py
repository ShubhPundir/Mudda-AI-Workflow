from .llm_service import LLMService
from .gemini_client import GeminiLLMAdapter

class LLMFactory:
    """
    Factory for creating LLMService instances.
    """

    @staticmethod
    def get_llm_service() -> LLMService:
        # Currently only Gemini is supported.
        return GeminiLLMAdapter()
