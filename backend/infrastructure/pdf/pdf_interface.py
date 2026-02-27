from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class PDFInterface(ABC):
    """
    Abstract interface for PDF generation services.
    """

    @abstractmethod
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
            metadata: Metadata dictionary containing 'title' and other info.
            filename: Optional filename.

        Returns:
            Dict containing file_path, filename, size_bytes, etc.
        """
        pass
