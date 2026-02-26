import os
import logging
from typing import Any, Dict
from google import genai
from google.genai import types

from .llm_service import LLMService

logger = logging.getLogger(__name__)

class GeminiLLMAdapter(LLMService):
    """
    Implementation of LLMService using Google Gemini.
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
            model='gemini-2.5-flash',
            contents=content
        )
        return response

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
