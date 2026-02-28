import os
from .llm_interface import LLMInterface
from .gemini_llm_adapter import GeminiLLMAdapter
from .bedrock_llm_adapter import BedrockLLMAdapter


class LLMFactory:
    """
    Factory for creating LLMInterface instances.
    Supports multiple LLM providers: Gemini, AWS Bedrock (Claude 3)
    
    Provider selection via LLM_PROVIDER environment variable:
    - "gemini" (default) - Google Gemini
    - "bedrock" - AWS Bedrock with Claude 3 Sonnet
    """
    _instance = None

    @classmethod
    def get_llm_service(cls) -> LLMInterface:
        """
        Get LLM service instance (singleton)
        
        Returns:
            LLMInterface implementation based on LLM_PROVIDER env var
        """
        if cls._instance is None:
            provider = os.getenv("LLM_PROVIDER", "gemini").lower()
            
            if provider == "bedrock":
                cls._instance = BedrockLLMAdapter()
            elif provider == "gemini":
                cls._instance = GeminiLLMAdapter()
            else:
                # Default to Gemini
                cls._instance = GeminiLLMAdapter()
        
        return cls._instance
    
    @classmethod
    def reset(cls):
        """Reset the singleton instance (useful for testing)"""
        cls._instance = None
