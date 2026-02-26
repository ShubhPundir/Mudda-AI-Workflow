"""
Document generation activities.

Uses LLMService for AI text generation and PDFGenerator for file creation.
AI calls are encapsulated here — never inside the workflow itself.
"""
import logging
from typing import Any, Dict
from temporalio import activity

from infrastructure import PDFFactory
from sessions.llm import LLMFactory
import logging

logger = logging.getLogger(__name__)

# Module-level instances
_llm_service = LLMFactory.get_llm_service()
_pdf_service = PDFFactory.get_pdf_service()
async def generate_report(input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a report document (AI text + PDF).

    Steps:
        1. Call LLMService to generate report text.
        2. Call PDFGenerator to create the PDF file.
        3. Return file path + metadata.

    Args:
        input: Dict containing:
            - problem_statement (str): The civic issue description.
            - context (dict, optional): Additional context from prior steps.
            - report_type (str, optional): 'summary' or 'detailed'.
            - step_id (str, optional): Originating workflow step ID.
            - title (str, optional): Report title.

    Returns:
        Structured JSON with file_path, filename, ai_metadata, etc.
    """
    step_id = input.get("step_id", "unknown")
    logger.info("generate_report activity — step_id=%s", step_id)

    # Step 1: Generate text via LLM
    report_text = await _llm_service.generate_report(input)

    # Step 2: Generate PDF
    metadata = {
        "title": input.get("title", f"Report — {input.get('problem_statement', 'Civic Issue')[:50]}"),
        "report_type": input.get("report_type", "summary"),
        "step_id": step_id,
    }
    pdf_result = await _pdf_service.generate(
        content=report_text,
        metadata=metadata,
    )

    logger.info(
        "Report generated — step_id=%s file=%s",
        step_id,
        pdf_result.get("file_path"),
    )

    return {
        "step_id": step_id,
        "status": "completed",
        "file_path": pdf_result["file_path"],
        "filename": pdf_result["filename"],
        "size_bytes": pdf_result["size_bytes"],
        "ai_metadata": {
            "report_type": input.get("report_type", "summary"),
            "report_length_chars": len(report_text),
            "model": "gemini-2.5-flash",
        },
    }
