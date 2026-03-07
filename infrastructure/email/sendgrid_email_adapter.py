import logging
from typing import Any, Dict
from .email_interface import EmailInterface

logger = logging.getLogger(__name__)

class SendGridEmailAdapter(EmailInterface):
    """
    Placeholder implementation of EmailInterface using SendGrid.
    """

    def __init__(self) -> None:
        logger.info("SendGridEmailInterface initialized (Placeholder)")

    async def send_email(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Sending email via SendGrid (Placeholder) — to=%s", payload.get("to"))
        # In a real implementation, you would use the sendgrid SDK here.
        return {
            "message_id": "sendgrid-placeholder-id",
            "status": "sent_placeholder",
            "to": payload.get("to"),
            "subject": payload.get("subject"),
        }
