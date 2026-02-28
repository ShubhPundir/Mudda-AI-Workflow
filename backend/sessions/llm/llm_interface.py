from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel

class LLMInterface(ABC):
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

    @abstractmethod
    async def generate_structured(
        self, 
        content: str, 
        response_schema: Type[BaseModel]
    ) -> BaseModel:
        """
        Generate structured output from the LLM with schema validation.
        
        Args:
            content: The prompt/content to send to the model
            response_schema: Pydantic model class defining the expected response structure
            
        Returns:
            Validated Pydantic model instance
            
        Raises:
            ValueError: If the response doesn't match the schema
        """
        pass
