"""
Notification activities for sending email/SMS/push notifications.

Uses the EmailAdapter from the infrastructure layer.
"""
import logging
from typing import Any, Dict
from temporalio import activity

from infrastructure.email_adapter import EmailAdapter

logger = logging.getLogger(__name__)

# Module-level adapter instance (re-used across activity invocations)
_email_adapter = EmailAdapter()


@activity.defn
async def send_notification(input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send a notification (currently email-based).

    Args:
        input: Dict containing:
            - to (str): Recipient address.
            - subject (str): Notification subject.
            - body (str): Notification body text.
            - cc (str, optional): CC recipient.
            - notification_type (str, optional): e.g. 'email', 'sms'.
            - step_id (str, optional): Originating workflow step ID.

    Returns:
        Structured JSON with delivery status.
    """
    step_id = input.get("step_id", "unknown")
    notification_type = input.get("notification_type", "email")

    logger.info(
        "Sending notification — step_id=%s type=%s to=%s",
        step_id,
        notification_type,
        input.get("to"),
    )

    if notification_type == "email":
        result = await _email_adapter.send(
            to=input.get("to", ""),
            subject=input.get("subject", "Mudda Workflow Notification"),
            body=input.get("body", ""),
            cc=input.get("cc"),
        )
    else:
        # Placeholder for SMS / push / other channels
        logger.warning("Unsupported notification type: %s — falling back to log", notification_type)
        result = {
            "status": "logged",
            "notification_type": notification_type,
            "message": f"Notification logged (type '{notification_type}' not yet implemented)",
        }

    return {
        "step_id": step_id,
        "notification_type": notification_type,
        "result": result,
        "status": "completed",
    }
