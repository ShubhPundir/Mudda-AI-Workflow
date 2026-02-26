from typing import Optional
from .pdf_service import PDFService
from .fpdf_pdf_adapter import FPDFPDFAdapter

class PDFFactory:
    """
    Factory for creating PDFService instances.
    """
    _instance = None

    @classmethod
    def get_pdf_service(cls, output_dir: Optional[str] = None) -> PDFService:
        if cls._instance is None:
            # Currently only FPDF is supported as per requirements.
            cls._instance = FPDFPDFAdapter(output_dir=output_dir)
        return cls._instance
