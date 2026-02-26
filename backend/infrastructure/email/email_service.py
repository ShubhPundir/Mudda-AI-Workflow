from abc import ABC, abstractmethod
from typing import Any, Dict

class EmailService(ABC):
    """
    Abstract interface for email services.
    """

    @abstractmethod
    async def send_email(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send an email.

        Args:
            payload: Dictionary containing email details (to, subject, body/html, etc.)

        Returns:
            Dictionary with delivery result (message_id, status, etc.)
        """
        pass
