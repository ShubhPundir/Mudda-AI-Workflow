"""
LLM service adapter for AI-powered text generation.

Encapsulates all Gemini / LLM API calls. This is the ONLY place
where LLM calls should originate — never inside a Temporal workflow.
No Temporal decorators — this is a plain infrastructure wrapper.
"""
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class LLMService:
    """
    Wraps the Gemini AI model for report / text generation.

    Uses the existing GeminiClient from sessions.gemini_client.
    """

    def __init__(self):
        # Lazy import to avoid import-time side effects when the module
        # is loaded by the Temporal worker (which may not need the LLM
        # for every activity).
        self._client = None

    def _get_client(self):
        """Lazy-initialise the Gemini client."""
        if self._client is None:
            from sessions.gemini_client import gemini_client
            self._client = gemini_client
        return self._client

    @staticmethod
    async def generate_report(inputs: Dict[str, Any]) -> str:
        """
        Generate a text report using the LLM.

        Args:
            inputs: Dict containing at minimum:
                - problem_statement (str): Description of the civic issue.
                - context (dict, optional): Additional context / prior results.
                - report_type (str, optional): e.g. 'summary', 'detailed'.

        Returns:
            Generated report text (str).

        Raises:
            RuntimeError: If the LLM call fails.
        """
        service = LLMService()
        client = service._get_client()

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

        logger.info(
            "LLM report generation — type=%s problem=%s",
            report_type,
            problem[:80],
        )

        try:
            response = await client.generate_async(prompt)
            report_text = response.text if hasattr(response, "text") else str(response)
            logger.info("LLM report generated — %d chars", len(report_text))
            return report_text
        except Exception as exc:
            logger.error("LLM generation failed: %s", exc, exc_info=True)
            raise RuntimeError(f"LLM report generation failed: {exc}") from exc
