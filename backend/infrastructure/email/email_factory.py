import logging
from config import settings
from .email_service import EmailService
from .resend_email_adapter import ResendEmailAdapter
from .aws_ses_email_adapter import AWSSESEmailAdapter
from .sendgrid_email_adapter import SendGridEmailAdapter
from .brevo_email_adapter import BrevoEmailAdapter

logger = logging.getLogger(__name__)

class EmailFactory:
    """
    Factory for creating EmailService instances.
    """

    @staticmethod
    def get_email_service() -> EmailService:
        provider = settings.EMAIL_PROVIDER.lower()
        
        if provider == "resend":
            return ResendEmailAdapter()
        elif provider == "aws_ses" or provider == "ses":
            return AWSSESEmailAdapter()
        elif provider == "sendgrid":
            return SendGridEmailAdapter()
        elif provider == "brevo":
            return BrevoEmailAdapter()
        else:
            logger.warning("Unknown email provider '%s', defaulting to Resend", provider)
            return ResendEmailAdapter()
