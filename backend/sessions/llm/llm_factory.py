from .llm_service import LLMService
from .gemini_client import GeminiLLMAdapter

class LLMFactory:
    """
    Factory for creating LLMService instances.
    """
    _instance = None

    @classmethod
    def get_llm_service(cls) -> LLMService:
        if cls._instance is None:
            # Currently only Gemini is supported.
            cls._instance = GeminiLLMAdapter()
        return cls._instance
