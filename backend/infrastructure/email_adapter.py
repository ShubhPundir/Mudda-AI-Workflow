"""
EmailAdapter — infrastructure layer wrapper around the Resend email API.

Design rules (infrastructure layer):
    - NO Temporal decorators (@activity.defn, etc.)
    - Plain async class, fully testable in isolation
    - All configuration read from environment / Settings at construction time
    - Raises on fatal errors; caller (activity) handles retries via Temporal

Resend Python SDK: https://resend.com/docs/send-with-python
"""
import logging
from typing import Any, Dict, List, Optional

import resend

from config import settings

logger = logging.getLogger(__name__)


class EmailAdapter:
    """
    Thin async wrapper around the Resend email API.

    Usage:
        adapter = EmailAdapter()
        result = await adapter.send_email({
            "to": ["user@example.com"],
            "subject": "Civic Issue Update",
            "body": "Your issue has been resolved.",
            "from_email": "noreply@yourdomain.com",   # optional override
        })
    """

    def __init__(self) -> None:
        api_key = settings.RESEND_API_KEY
        if not api_key:
            logger.warning(
                "RESEND_API_KEY is not configured — email sending will fail at runtime. "
                "Set RESEND_API_KEY in your .env file or environment variables."
            )
        else:
            # Resend SDK is configured globally for the process.
            resend.api_key = api_key

        self.default_from_email: str = settings.EMAIL_FROM_ADDRESS
        self.default_from_name: str = settings.EMAIL_FROM_NAME

        logger.info(
            "EmailAdapter initialised — from=%s <%s>",
            self.default_from_name,
            self.default_from_email,
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def send_email(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a transactional email via Resend.

        Args:
            payload: Dict containing:
                - to (list[str] | str): Recipient address(es). Required.
                - subject (str): Email subject line. Required.
                - body (str): Plain-text body. Required unless html is provided.
                - html (str, optional): HTML body. Takes precedence over body.
                - from_email (str, optional): Sender address override.
                - from_name (str, optional): Sender display-name override.
                - reply_to (str, optional): Reply-to address.
                - cc (list[str], optional): CC addresses.
                - bcc (list[str], optional): BCC addresses.
                - tags (list[dict], optional): Resend tags, e.g. [{"name": "k", "value": "v"}].

        Returns:
            Dict with keys: message_id, status, to, subject.

        Raises:
            ValueError: When required fields are missing.
            resend.exceptions.ResendError: On Resend API errors.
        """
        to: List[str] = self._normalise_recipients(payload.get("to"))
        subject: str = payload.get("subject", "").strip()
        body_text: Optional[str] = payload.get("body")
        body_html: Optional[str] = payload.get("html")

        if not to:
            raise ValueError("EmailAdapter.send_email: 'to' field is required")
        if not subject:
            raise ValueError("EmailAdapter.send_email: 'subject' field is required")
        if not body_text and not body_html:
            raise ValueError(
                "EmailAdapter.send_email: either 'body' (text) or 'html' is required"
            )

        # Build sender string
        from_name = payload.get("from_name", self.default_from_name)
        from_email = payload.get("from_email", self.default_from_email)
        sender = f"{from_name} <{from_email}>" if from_name else from_email

        # Compose the Resend params dict
        params: Dict[str, Any] = {
            "from": sender,
            "to": to,
            "subject": subject,
        }

        if body_html:
            params["html"] = body_html
        else:
            params["text"] = body_text  # type: ignore[assignment]

        if payload.get("reply_to"):
            params["reply_to"] = payload["reply_to"]
        if payload.get("cc"):
            params["cc"] = self._normalise_recipients(payload["cc"])
        if payload.get("bcc"):
            params["bcc"] = self._normalise_recipients(payload["bcc"])
        if payload.get("tags"):
            params["tags"] = payload["tags"]
        if payload.get("attachments"):
            # Resend attachments: [{"content": b64, "filename": "x.pdf"}, {"path": "path/to/file"}]
            params["attachments"] = payload["attachments"]

        logger.info(
            "Sending email via Resend — to=%s subject=%r attachment_count=%d",
            to,
            subject,
            len(payload.get("attachments", [])),
        )

        # Resend SDK is synchronous under the hood but very fast.
        # We call it directly here; Temporal handles retries at the activity level.
        email_response = resend.Emails.send(params)

        message_id: str = email_response.get("id", "")
        logger.info("Email sent — message_id=%s to=%s", message_id, to)

        return {
            "message_id": message_id,
            "status": "sent",
            "to": to,
            "subject": subject,
            "from": sender,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalise_recipients(value: Any) -> List[str]:
        """Accept a string or list and return a clean list of strings."""
        if value is None:
            return []
        if isinstance(value, str):
            return [value.strip()] if value.strip() else []
        if isinstance(value, (list, tuple)):
            return [str(v).strip() for v in value if str(v).strip()]
        return []
