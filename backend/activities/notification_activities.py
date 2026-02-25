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
from typing import Any, Dict

from temporalio import activity

from infrastructure.email_adapter import EmailAdapter

logger = logging.getLogger(__name__)

# Module-level adapter instance (created once per worker process)
_email_adapter = EmailAdapter()


@activity.defn
async def send_notification(input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send an email notification via the Resend API.

    This activity delegates all real work to EmailAdapter — it is purely
    a Temporal boundary, adding structured logging and a normalised return value.

    Args:
        input: Dict containing:
            - to (list[str] | str): Recipient address(es). Required.
            - subject (str): Email subject. Required.
            - body (str): Plain-text message body. Required unless `html` provided.
            - html (str, optional): HTML body. Takes precedence over `body`.
            - from_email (str, optional): Override the default sender address.
            - from_name (str, optional): Override the default sender display name.
            - reply_to (str, optional): Reply-to address.
            - cc (list[str], optional): CC recipients.
            - bcc (list[str], optional): BCC recipients.
            - tags (list[dict], optional): Resend metadata tags.
            - step_id (str, optional): Originating workflow step ID (for tracing).
            - issue_id (str, optional): Related civic issue ID (for tracing).

    Returns:
        Dict with keys:
            - step_id (str)
            - status (str): "completed"
            - channel (str): "email"
            - message_id (str): Resend message ID
            - to (list[str])
            - subject (str)
    """
    step_id: str = input.get("step_id", "unknown")
    issue_id: str = input.get("issue_id", "unknown")

    activity.logger.info(
        "send_notification activity — step_id=%s issue_id=%s to=%s subject=%r",
        step_id,
        issue_id,
        input.get("to"),
        input.get("subject"),
    )

    result = await _email_adapter.send_email(input)

    activity.logger.info(
        "Email delivered — step_id=%s message_id=%s",
        step_id,
        result.get("message_id"),
    )

    return {
        "step_id": step_id,
        "status": "completed",
        "channel": "email",
        "message_id": result["message_id"],
        "to": result["to"],
        "subject": result["subject"],
    }
