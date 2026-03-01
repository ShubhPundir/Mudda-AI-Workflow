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
from sessions.llm import LLMFactory
from schemas.activity_schemas import SendNotificationInput, SendNotificationOutput

logger = logging.getLogger(__name__)

# Module-level adapter instances (created once per worker process)
_email_service = EmailFactory.get_email_service()
_llm_service = LLMFactory.get_llm_service()


@activity.defn
async def send_notification(input: SendNotificationInput) -> SendNotificationOutput:
    """
    Send an email notification via the Resend API with LLM-enhanced content generation.

    This activity delegates all real work to EmailAdapter — it is purely
    a Temporal boundary, adding structured logging and a normalised return value.
    LLM service is available for content enhancement if needed.

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

    # Generate LLM-enhanced email content if body/html is not provided
    email_data = input.model_dump()
    if not input.body and not input.html:
        prompt = f"Generate a professional email body for the following subject: {input.subject}"
        if input.issue_id and input.issue_id != "unknown":
            prompt += f" (Issue ID: {input.issue_id})"
        
        activity.logger.info("Generating LLM-enhanced email content")
        generated_content = await _llm_service.generate_report({"problem_statement": prompt})
        email_data["body"] = generated_content

    result = await _email_service.send_email(email_data)

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
