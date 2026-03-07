import logging
from config import settings
from .email_interface import EmailInterface
from .resend_email_adapter import ResendEmailAdapter
from .aws_ses_email_adapter import AWSSESEmailAdapter
from .sendgrid_email_adapter import SendGridEmailAdapter
from .brevo_email_adapter import BrevoEmailAdapter

logger = logging.getLogger(__name__)

class EmailFactory:
    """
    Factory for creating EmailInterface instances.
    """
    _instance = None

    @classmethod
    def get_email_service(cls) -> EmailInterface:
        if cls._instance is not None:
            return cls._instance
            
        provider = settings.EMAIL_PROVIDER.lower()
        
        if provider == "resend":
            cls._instance = ResendEmailAdapter()
        elif provider == "aws_ses" or provider == "ses":
            cls._instance = AWSSESEmailAdapter()
        elif provider == "sendgrid":
            cls._instance = SendGridEmailAdapter()
        elif provider == "brevo":
            cls._instance = BrevoEmailAdapter()
        else:
            logger.warning("Unknown email provider '%s', defaulting to Resend", provider)
            cls._instance = ResendEmailAdapter()
            
        return cls._instance
