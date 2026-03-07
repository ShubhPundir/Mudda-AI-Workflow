from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel
from schemas.activity_schemas import PDFServiceInput, SendNotificationInput

class LLMInterface(ABC):
    """
    Abstract interface for LLM services.
    """

    async def generate_report(self, input: PDFServiceInput) -> str:
        """
        Generate a text report using an LLM.
        Standard prompt logic for document reports.

        Args:
            input: PDFServiceInput schema.

        Returns:
            Generated report text.
        """
        report_type = input.report_type or "summary"
        content = input.content
        title = input.title 
        problem_statement = input.problem_statement or "No problem statement provided"

        prompt = (
            f"Generate a {report_type} report for the following civic issue:\n\n"
            f"Issue: {problem_statement}\n\n"
        )

        if title:
            prompt += f"Title: {title}\n\n"

        if content:
            prompt += f"Content: {content}\n\n"

        prompt += (
            "Provide a clear, structured report with findings, "
            "recommendations, and next steps."
        )

        return await self.generate_async(prompt)

    async def generate_email(self, input: SendNotificationInput) -> str:
        """
        Generate a professional email with subject and body using an LLM.

        Args:
            input: SendNotificationInput schema.

        Returns:
            Generated email text with SUBJECT: and BODY: markers.
        """
        content = input.content
        issue_id = input.issue_id

        prompt = f"""Generate a professional email with subject and body.

Content description: {content}

Issue ID: {issue_id}

Format your response as:
SUBJECT: [email subject here]
BODY: [email body here]"""

        return await self.generate_async(prompt)

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
