from abc import ABC, abstractmethod
from typing import Any, Dict

class LLMService(ABC):
    """
    Abstract interface for LLM services.
    """

    @abstractmethod
    async def generate_report(self, inputs: Dict[str, Any]) -> str:
        """
        Generate a text report using an LLM.

        Args:
            inputs: Dict containing problem_statement, context, report_type, etc.

        Returns:
            Generated report text.
        """
        pass

    @abstractmethod
    async def generate_async(self, content: str) -> Any:
        """
        Generate raw content from the LLM asynchronously.
        
        Args:
            content: The prompt/content to send to the model
            
        Returns:
            Provider-specific response object
        """
        pass
