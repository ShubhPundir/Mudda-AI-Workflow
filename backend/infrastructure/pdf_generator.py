"""
PDF document generator using fpdf2.

Architecture:
    Workflow  →  [Temporal Activity]  →  PDFGenerator (this file)
                                            ↓
                                         fpdf2 library

Design rules:
    - NO Temporal decorators (@activity.defn, etc.)
    - Clean infrastructure wrapper, fully testable in isolation.
    - Structured output: Title, Date, and Body text.
"""
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from fpdf import FPDF, XPos, YPos

logger = logging.getLogger(__name__)


class PDFGenerator:
    """
    Generates PDF documents using the fpdf2 library.

    Usage:
        generator = PDFGenerator()
        result = await generator.generate(
            content="Issue: Water leakage at street 10",
            metadata={"title": "Civic Issue Report", "report_type": "summary"}
        )
    """

    def __init__(self, output_dir: Optional[str] = None):
        """
        Args:
            output_dir: Directory to save generated PDFs.
                        Defaults to '<cwd>/generated_reports'.
        """
        self.output_dir = output_dir or os.path.join(os.getcwd(), "generated_reports")
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info("PDFGenerator initialised — output_dir=%s", self.output_dir)

    async def generate(
        self,
        content: str,
        metadata: Dict[str, Any],
        filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a PDF document from text content.

        Args:
            content: The text content of the report.
            metadata: Metadata dictionary containing 'title'.
            filename: Optional filename. If omitted, generated from title.

        Returns:
            Dict containing: file_path, filename, size_bytes.
        """
        title = metadata.get("title", "Civic Issue Report")
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create safe filename
        safe_title = "".join(c if c.isalnum() or c in "-_ " else "" for c in title)
        filename = filename or f"{safe_title.replace(' ', '_').lower()}.pdf"
        file_path = os.path.join(self.output_dir, filename)

        logger.info("Generating real PDF — title=%r file=%s", title, filename)

        try:
            # Initialize PDF
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            # --- Header ---
            pdf.set_font("helvetica", "B", 16)
            pdf.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
            pdf.set_font("helvetica", "I", 10)
            pdf.cell(0, 10, f"Generated on: {date_str}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
            pdf.ln(10)
            
            # --- Body ---
            pdf.set_font("helvetica", "", 12)
            # multi_cell is perfect for long text blocks
            pdf.multi_cell(0, 10, content)
            
            # --- Footer ---
            # Page number at the bottom automatically handled by fpdf or we can footer override
            # Here we just save
            pdf.output(file_path)

            size_bytes = os.path.getsize(file_path)
            logger.info("PDF saved successfully — %d bytes", size_bytes)

            return {
                "file_path": file_path,
                "filename": filename,
                "size_bytes": size_bytes,
                "generated_at": date_str,
                "metadata": metadata
            }

        except Exception as exc:
            logger.error("Failed to generate PDF: %s", exc, exc_info=True)
            raise RuntimeError(f"PDF generation failed: {exc}") from exc
