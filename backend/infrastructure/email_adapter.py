"""
Email adapter for sending notifications.

Integrate your email provider (SES, SendGrid, SMTP, etc.) here.
No Temporal decorators — this is a plain infrastructure wrapper.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class EmailAdapter:
    """
    Thin wrapper around an email delivery service.

    Replace the placeholder implementation with your actual email provider
    (e.g., AWS SES, SendGrid, Mailgun, or SMTP).
    """

    def __init__(self, provider: str = "console"):
        """
        Args:
            provider: Email provider identifier. Defaults to 'console' (logs only).
        """
        self.provider = provider

    async def send(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        html_body: Optional[str] = None,
    ) -> dict:
        """
        Send an email notification.

        Args:
            to: Recipient email address.
            subject: Email subject line.
            body: Plain-text email body.
            cc: Optional CC recipient.
            bcc: Optional BCC recipient.
            html_body: Optional HTML body (sent alongside plain text).

        Returns:
            Dict with delivery status and metadata.

        Raises:
            RuntimeError: If the email provider fails.
        """
        logger.info(
            "Sending email via %s — to=%s subject=%s",
            self.provider,
            to,
            subject,
        )

        # ------------------------------------------------------------------
        # TODO: Replace with real provider integration, e.g.:
        #
        # if self.provider == "ses":
        #     import boto3
        #     client = boto3.client("ses")
        #     response = client.send_email(...)
        #     return {"status": "sent", "message_id": response["MessageId"]}
        # ------------------------------------------------------------------

        # Placeholder: log-only delivery
        logger.info("Email body preview: %s", body[:200])

        return {
            "status": "sent",
            "provider": self.provider,
            "to": to,
            "subject": subject,
        }
