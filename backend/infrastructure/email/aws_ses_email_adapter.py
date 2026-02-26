import logging
import boto3
from botocore.exceptions import ClientError
from typing import Any, Dict, List
from .email_service import EmailService, EmailPayload
from config import settings

logger = logging.getLogger(__name__)

class AWSSESEmailAdapter(EmailService):
    """
    Implementation of EmailService using AWS SES.
    """

    def __init__(self) -> None:
        self.client = boto3.client(
            'ses',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.default_from_email: str = settings.EMAIL_FROM_ADDRESS
        self.default_from_name: str = settings.EMAIL_FROM_NAME
        logger.info("AWSSESEmailAdapter initialized")

    async def send_email(self, payload: EmailPayload) -> Dict[str, Any]:
        to: List[str] = self._normalise_recipients(payload.get("to"))
        subject: str = (payload.get("subject") or "").strip()
        body_text: str = payload.get("body", "")
        body_html: str = payload.get("html", "")

        # Validation
        if not to:
            raise ValueError("AWSSESEmailAdapter.send_email: Recipient list is empty")
        if not subject:
            raise ValueError("AWSSESEmailAdapter.send_email: Email subject is empty")
        if not body_text and not body_html:
            raise ValueError("AWSSESEmailAdapter.send_email: Either 'body' or 'html' must be provided")

        from_name = payload.get("from_name", self.default_from_name)
        from_email = payload.get("from_email", self.default_from_email)
        sender = f"{from_name} <{from_email}>" if from_name else from_email

        # Build message
        destination = {'ToAddresses': to}
        if payload.get("cc"):
            destination['CcAddresses'] = self._normalise_recipients(payload["cc"])
        if payload.get("bcc"):
            destination['BccAddresses'] = self._normalise_recipients(payload["bcc"])

        message = {
            'Subject': {'Data': subject},
            'Body': {}
        }
        if body_html:
            message['Body']['Html'] = {'Data': body_html}
        if body_text:
            message['Body']['Text'] = {'Data': body_text}

        try:
            logger.info("Sending email via AWS SES — to=%s subject=%r", to, subject)
            response = self.client.send_email(
                Source=sender,
                Destination=destination,
                Message=message,
            )
            return {
                "message_id": response['MessageId'],
                "status": "sent",
                "to": to,
                "subject": subject,
            }
        except ClientError as e:
            logger.error("AWS SES send failed: %s", e.response['Error']['Message'])
            raise RuntimeError(f"AWS SES send failed: {e.response['Error']['Message']}")

    @staticmethod
    def _normalise_recipients(value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value.strip()] if value.strip() else []
        if isinstance(value, (list, tuple)):
            return [str(v).strip() for v in value if str(v).strip()]
        return []
