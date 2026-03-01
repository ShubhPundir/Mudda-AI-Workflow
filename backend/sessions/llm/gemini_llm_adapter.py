import os
import logging
import json
from typing import Any, Dict, Type
from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError

from .llm_interface import LLMInterface

logger = logging.getLogger(__name__)

class GeminiLLMAdapter(LLMInterface):
    """
    Implementation of LLMInterface using Google Gemini.
    Supports structured output with JSON schema validation.
    """

    def __init__(self):
        self.client = None
        self._initialize_gemini()

    def _initialize_gemini(self):
        """Initialize Gemini AI client"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY environment variable is not set. LLM features may fail.")
            return
        
        self.client = genai.Client(api_key=api_key)

    async def generate_async(self, content: str) -> Any:
        """
        Generate content using the Gemini model asynchronously
        """
        if not self.client:
            raise ValueError("Gemini client is not initialized (missing API key?)")
        
        response = await self.client.aio.models.generate_content(
            model='gemini-3-flash',
            contents=content
        )
        return response

    async def generate_structured(
        self, 
        content: str, 
        response_schema: Type[BaseModel]
    ) -> BaseModel:
        """
        Generate structured output with JSON schema validation.
        Uses Gemini's native JSON mode for reliable structured output.
        
        Args:
            content: The prompt/content to send to the model
            response_schema: Pydantic model class defining expected structure
            
        Returns:
            Validated Pydantic model instance
            
        Raises:
            ValueError: If client not initialized or validation fails
            ValidationError: If response doesn't match schema
        """
        if not self.client:
            raise ValueError("Gemini client is not initialized (missing API key?)")
        
        # Convert Pydantic schema to JSON schema for Gemini
        json_schema = response_schema.model_json_schema()
        
        try:
            # Use Gemini's structured output with JSON schema
            response = await self.client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents=content,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=json_schema
                )
            )
            
            # Extract JSON text from response
            response_text = response.text if hasattr(response, "text") else str(response)
            
            # Parse and validate with Pydantic
            response_data = json.loads(response_text)
            validated_response = response_schema.model_validate(response_data)
            
            logger.info(
                "Structured output generated successfully for schema: %s",
                response_schema.__name__
            )
            return validated_response
            
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse JSON from Gemini response: %s", exc)
            raise ValueError(f"Invalid JSON response from model: {exc}") from exc
        except ValidationError as exc:
            logger.error("Response validation failed: %s", exc)
            raise
        except Exception as exc:
            logger.error("Structured generation failed: %s", exc)
            raise RuntimeError(f"Structured output generation failed: {exc}") from exc

    async def generate_report(self, inputs: Dict[str, Any]) -> str:
        problem = inputs.get("problem_statement", "")
        context = inputs.get("context", {})
        report_type = inputs.get("report_type", "summary")

        prompt = (
            f"Generate a {report_type} report for the following civic issue:\n\n"
            f"Issue: {problem}\n\n"
        )
        if context:
            prompt += f"Additional context:\n{context}\n\n"
        prompt += (
            "Provide a clear, structured report with findings, "
            "recommendations, and next steps."
        )

        logger.info("LLM report generation via Gemini — type=%s", report_type)

        try:
            response = await self.generate_async(prompt)
            report_text = response.text if hasattr(response, "text") else str(response)
            return report_text
        except Exception as exc:
            logger.error("LLM generation failed: %s", exc)
            raise RuntimeError(f"LLM report generation failed: {exc}") from exc
