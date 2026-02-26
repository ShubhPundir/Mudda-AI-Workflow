import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional
from fpdf import FPDF, XPos, YPos
from .pdf_service import PDFService

logger = logging.getLogger(__name__)

class FPDFPDFAdapter(PDFService):
    """
    Implementation of PDFService using the fpdf2 library.
    """

    def __init__(self, output_dir: Optional[str] = None):
        """
        Args:
            output_dir: Directory to save generated PDFs.
        """
        self.output_dir = output_dir or os.path.join(os.getcwd(), "generated_reports")
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info("FPDFPDFAdapter initialised — output_dir=%s", self.output_dir)

    async def generate(
        self,
        content: str,
        metadata: Dict[str, Any],
        filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        title = metadata.get("title", "Civic Issue Report")
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        safe_title = "".join(c if c.isalnum() or c in "-_ " else "" for c in title)
        filename = filename or f"{safe_title.replace(' ', '_').lower()}.pdf"
        file_path = os.path.join(self.output_dir, filename)

        logger.info("Generating PDF via FPDF — title=%r file=%s", title, filename)

        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            pdf.set_font("helvetica", "B", 16)
            pdf.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
            pdf.set_font("helvetica", "I", 10)
            pdf.cell(0, 10, f"Generated on: {date_str}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
            pdf.ln(10)
            
            pdf.set_font("helvetica", "", 12)
            pdf.multi_cell(0, 10, content)
            
            pdf.output(file_path)

            size_bytes = os.path.getsize(file_path)
            return {
                "file_path": file_path,
                "filename": filename,
                "size_bytes": size_bytes,
                "generated_at": date_str,
                "metadata": metadata
            }

        except Exception as exc:
            logger.error("Failed to generate PDF: %s", exc)
            raise RuntimeError(f"PDF generation failed: {exc}") from exc
