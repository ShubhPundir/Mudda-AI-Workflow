from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypedDict

class EmailPayload(TypedDict, total=False):
    to: Any  # List[str] or str
    subject: str
    body: str
    html: str
    from_email: str
    from_name: str
    reply_to: str
    reply_to_name: str
    cc: Any  # List[str] or str
    bcc: Any  # List[str] or str
    tags: List[Dict[str, str]]
    attachments: List[Dict[str, Any]]
    step_id: str
    issue_id: str

class EmailInterface(ABC):
    """
    Abstract interface for email services.
    """

    @abstractmethod
    async def send_email(self, payload: EmailPayload) -> Dict[str, Any]:
        """
        Send an email.

        Args:
            payload: EmailPayload dictionary containing email details.

        Returns:
            Dictionary with delivery result (message_id, status, etc.)
        """
        pass
