import logging
import httpx
from typing import Any, Dict, List, Optional
from .email_interface import EmailInterface, EmailPayload
from config import settings

logger = logging.getLogger(__name__)

class BrevoEmailAdapter(EmailInterface):
    """
    Implementation of EmailInterface using Brevo (formerly Sendinblue) HTTP API.
    """

    def __init__(self) -> None:
        self.api_key = settings.BREVO_API_KEY
        self.base_url = "https://api.brevo.com/v3/smtp/email"
        self.default_from_email: str = settings.EMAIL_FROM_ADDRESS
        self.default_from_name: str = settings.EMAIL_FROM_NAME
        
        if not self.api_key:
            logger.warning("BREVO_API_KEY is not configured.")

    async def send_email(self, payload: EmailPayload) -> Dict[str, Any]:
        to: List[str] = self._normalise_recipients(payload.get("to"))
        subject: str = (payload.get("subject") or "").strip()
        body_text: Optional[str] = payload.get("body")
        body_html: Optional[str] = payload.get("html")

        # Validation
        if not to:
            raise ValueError("BrevoEmailAdapter.send_email: Recipient list is empty ('to')")
        if not subject:
            raise ValueError("BrevoEmailAdapter.send_email: Email subject is empty")
        if not body_text and not body_html:
            raise ValueError("BrevoEmailAdapter.send_email: Either 'body' or 'html' must be provided")

        from_name = payload.get("from_name", self.default_from_name)
        from_email = payload.get("from_email", self.default_from_email)

        # Brevo API format
        data: Dict[str, Any] = {
            "sender": {"name": from_name, "email": from_email},
            "to": [{"email": email} for email in to],
            "subject": subject,
        }

        if body_html:
            data["htmlContent"] = body_html
        if body_text:
            data["textContent"] = body_text

        if payload.get("cc"):
            data["cc"] = [{"email": email} for email in self._normalise_recipients(payload["cc"])]
        if payload.get("bcc"):
            data["bcc"] = [{"email": email} for email in self._normalise_recipients(payload["bcc"])]
        
        if payload.get("reply_to"):
            data["replyTo"] = {
                "email": payload["reply_to"],
                "name": payload.get("reply_to_name", "")
            }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": self.api_key
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            logger.info("Sending email via Brevo — to=%s subject=%r", to, subject)
            try:
                response = await client.post(self.base_url, headers=headers, json=data)
                
                if response.status_code >= 400:
                    logger.error("Brevo API error (%d): %s", response.status_code, response.text)
                    raise RuntimeError(f"Brevo send failed ({response.status_code}): {response.text}")
                
                result = response.json()
                # Support multiple message ID keys
                message_id = result.get("messageId") or result.get("message_id", "unknown")
                
                return {
                    "message_id": message_id,
                    "status": "sent",
                    "to": to,
                    "subject": subject,
                }
            except httpx.RequestError as exc:
                logger.error("Network error while calling Brevo: %s", exc)
                raise RuntimeError(f"Brevo connection failed: {exc}")

    @staticmethod
    def _normalise_recipients(value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value.strip()] if value.strip() else []
        if isinstance(value, (list, tuple)):
            return [str(v).strip() for v in value if str(v).strip()]
        return []
