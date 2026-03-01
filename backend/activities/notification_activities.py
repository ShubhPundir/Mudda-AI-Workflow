"""
Notification activities — Temporal activity layer for sending emails.

Architecture:
    Workflow  →  [Temporal]  →  send_notification (this file)
                                    ↓
                             EmailAdapter  →  Resend API

This file owns the @activity.defn decorator.
EmailAdapter (infrastructure layer) owns the actual API call.
"""
import logging
from temporalio import activity
from infrastructure import EmailFactory
from schemas.activity_schemas import SendNotificationInput, SendNotificationOutput

logger = logging.getLogger(__name__)

# Module-level adapter instance (created once per worker process)
_email_service = EmailFactory.get_email_service()


@activity.defn
async def send_notification(input: SendNotificationInput) -> SendNotificationOutput:
    """
    Send an email notification via the Resend API.

    This activity delegates all real work to EmailAdapter — it is purely
    a Temporal boundary, adding structured logging and a normalised return value.

    Args:
        input: SendNotificationInput containing email details.

    Returns:
        SendNotificationOutput with delivery confirmation.
    """
    activity.logger.info(
        "send_notification activity — step_id=%s issue_id=%s to=%s subject=%r",
        input.step_id,
        input.issue_id,
        input.to,
        input.subject,
    )

    result = await _email_service.send_email(input.model_dump())

    activity.logger.info(
        "Email delivered — step_id=%s message_id=%s",
        input.step_id,
        result.get("message_id"),
    )

    return SendNotificationOutput(
        step_id=input.step_id,
        status="completed",
        channel="email",
        message_id=result["message_id"],
        to=result["to"],
        subject=result["subject"],
    )
