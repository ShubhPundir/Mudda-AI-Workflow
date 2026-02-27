from .llm_interface import LLMInterface
from .gemini_llm_adapter import GeminiLLMAdapter

class LLMFactory:
    """
    Factory for creating LLMInterface instances.
    """
    _instance = None

    @classmethod
    def get_llm_service(cls) -> LLMInterface:
        if cls._instance is None:
            # Currently only Gemini is supported.
            cls._instance = GeminiLLMAdapter()
        return cls._instance
