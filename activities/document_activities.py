"""
Document generation activities.

Uses LLMService for AI text generation and PDFGenerator for file creation.
AI calls are encapsulated here — never inside the workflow itself.
"""
import logging
from temporalio import activity

from infrastructure import PDFFactory, S3Service
from sessions.llm import LLMFactory
from schemas.activity_schemas import PDFServiceInput, PDFServiceOutput
from config import settings

logger = logging.getLogger(__name__)

# Module-level instances
_llm_service = LLMFactory.get_llm_service()
_pdf_service = PDFFactory.get_pdf_service()

@activity.defn
async def pdf_service_activity(input: PDFServiceInput) -> PDFServiceOutput:
    """
    Generate a report document (AI text + PDF) and upload to S3 with intelligent data forwarding.

    Steps:
        1. Call LLMService to generate report text with context awareness.
        2. Call PDFGenerator to create the PDF file.
        3. Upload PDF to S3.
        4. Return file path, S3 URL, metadata, and extracted key points for downstream activities.
    """
    logger.info("pdf_service_activity — step_id=%s", input.step_id)

    # Step 1: Generate text via LLM with enhanced context
    report_text = await _llm_service.generate_report(input)

    # Step 2: Generate PDF
    metadata = {
        "title": input.title or f"Report - {input.content[:50]}",
        "report_type": input.report_type,
        "step_id": input.step_id,
    }
    pdf_result = await _pdf_service.generate(
        content=report_text,
        metadata=metadata,
    )

    # Step 3: Upload to S3
    s3_url = await S3Service.upload_document(pdf_result["file_path"])

    # Convert internal S3 URL to public HTTPS URL
    public_url = s3_url
    if s3_url.startswith("s3://"):
        s3_path = s3_url[len("s3://") :]
        bucket, _, key = s3_path.partition("/")
        if bucket and key:
            public_url = f"https://{bucket}.s3.ap-south-1.amazonaws.com/{key}"

    logger.info(
        "Report generated and uploaded — step_id=%s file=%s s3=%s",
        input.step_id,
        pdf_result.get("file_path"),
        public_url,
    )

    return PDFServiceOutput(
        step_id=input.step_id,
        status="completed",
        file_path=pdf_result["file_path"],
        s3_url=public_url,
        filename=pdf_result["filename"],
        size_bytes=pdf_result["size_bytes"],
        ai_metadata={
            "report_type": input.report_type,
            "report_length_chars": len(report_text),
            "model": settings.LLM_PROVIDER.lower(), 
        },
    )
