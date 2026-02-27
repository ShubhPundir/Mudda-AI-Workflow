from typing import Optional
from .pdf_interface import PDFInterface
from .fpdf_pdf_adapter import FPDFPDFAdapter

class PDFFactory:
    """
    Factory for creating PDFInterface instances.
    """
    _instance = None

    @classmethod
    def get_pdf_service(cls, output_dir: Optional[str] = None) -> PDFInterface:
        if cls._instance is None:
            # Currently only FPDF is supported as per requirements.
            cls._instance = FPDFPDFAdapter(output_dir=output_dir)
        return cls._instance
