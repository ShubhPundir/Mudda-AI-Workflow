from typing import Optional
from .pdf_service import PDFService
from .fpdf_pdf_adapter import FPDFPDFAdapter

class PDFFactory:
    """
    Factory for creating PDFService instances.
    """

    @staticmethod
    def get_pdf_service(output_dir: Optional[str] = None) -> PDFService:
        # Currently only FPDF is supported as per requirements.
        return FPDFPDFAdapter(output_dir=output_dir)
