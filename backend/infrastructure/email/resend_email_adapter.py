import logging
import os
from typing import Any, Dict, List, Optional
import resend
from config import settings
from .email_interface import EmailInterface, EmailPayload

logger = logging.getLogger(__name__)

class ResendEmailAdapter(EmailInterface):
    """
    Implementation of EmailInterface using Resend API.
    """

    def __init__(self) -> None:
        api_key = settings.RESEND_API_KEY
        if not api_key:
            logger.warning(
                "RESEND_API_KEY is not configured — email sending will fail at runtime."
            )
        else:
            resend.api_key = api_key

        self.default_from_email: str = settings.EMAIL_FROM_ADDRESS
        self.default_from_name: str = settings.EMAIL_FROM_NAME

    async def send_email(self, payload: EmailPayload) -> Dict[str, Any]:
        to: List[str] = self._normalise_recipients(payload.get("to"))
        subject: str = (payload.get("subject") or "").strip()
        body_text: Optional[str] = payload.get("body")
        body_html: Optional[str] = payload.get("html")

        if not to:
            raise ValueError("ResendEmailAdapter.send_email: Recipient list is empty")
        if not subject:
            raise ValueError("ResendEmailAdapter.send_email: Email subject is empty")
        if not body_text and not body_html:
            raise ValueError(
                "ResendEmailAdapter.send_email: either 'body' (text) or 'html' is required"
            )

        from_name = payload.get("from_name", self.default_from_name)
        from_email = payload.get("from_email", self.default_from_email)
        sender = f"{from_name} <{from_email}>" if from_name else from_email

        params: Dict[str, Any] = {
            "from": sender,
            "to": to,
            "subject": subject,
        }

        if body_html:
            params["html"] = body_html
        else:
            params["text"] = body_text

        if payload.get("reply_to"):
            params["reply_to"] = payload["reply_to"]
        if payload.get("cc"):
            params["cc"] = self._normalise_recipients(payload["cc"])
        if payload.get("bcc"):
            params["bcc"] = self._normalise_recipients(payload["bcc"])
        if payload.get("tags"):
            params["tags"] = payload["tags"]
        if payload.get("attachments"):
            processed_attachments = []
            for att in payload["attachments"]:
                if "path" in att and not att["path"].startswith(("http://", "https://")):
                    try:
                        with open(att["path"], "rb") as f:
                            content_bytes = list(f.read())
                            processed_attachments.append({
                                "filename": att.get("filename", os.path.basename(att["path"])),
                                "content": content_bytes
                            })
                    except Exception as e:
                        logger.error("Failed to read attachment at %s: %s", att["path"], e)
                        raise ValueError(f"Could not read attachment file: {att['path']}")
                else:
                    processed_attachments.append(att)
            params["attachments"] = processed_attachments

        logger.info("Sending email via Resend — to=%s subject=%r", to, subject)
        email_response = resend.Emails.send(params)
        message_id: str = email_response.get("id", "")

        return {
            "message_id": message_id,
            "status": "sent",
            "to": to,
            "subject": subject,
            "from": sender,
        }

    @staticmethod
    def _normalise_recipients(value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value.strip()] if value.strip() else []
        if isinstance(value, (list, tuple)):
            return [str(v).strip() for v in value if str(v).strip()]
        return []
