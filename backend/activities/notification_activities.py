"""
Notification activities — Temporal activity layer for sending emails.

Architecture:
    Workflow  →  [Temporal]  →  send_notification (this file)
                                    ↓
                             LLM generates email content
                                    ↓
                             EmailAdapter  →  Email API

This file owns the @activity.defn decorator.
LLM generates subject and body based on content description.
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
    Send an email notification with LLM-generated content.

    The LLM generates both subject and body based on the content description.

    Args:
        input: SendNotificationInput containing recipient and content description.

    Returns:
        SendNotificationOutput with delivery confirmation.
    """
    activity.logger.info(
        "send_notification activity — step_id=%s issue_id=%s to=%s",
        input.step_id,
        input.issue_id,
        input.to,
    )

    # Generate email subject and body using LLM
    activity.logger.info("Generating email content via LLM")
    
    prompt = f"""Generate a professional email with subject and body.

Content description: {input.content}

Issue ID: {input.issue_id}

Format your response as:
SUBJECT: [email subject here]
BODY: [email body here]"""

    llm_response = await _llm_service.generate_report({"problem_statement": prompt})
    
    # Parse LLM response to extract subject and body
    subject = ""
    body = ""
    
    lines = llm_response.strip().split('\n')
    current_section = None
    
    for line in lines:
        if line.startswith('SUBJECT:'):
            current_section = 'subject'
            subject = line.replace('SUBJECT:', '').strip()
        elif line.startswith('BODY:'):
            current_section = 'body'
            body = line.replace('BODY:', '').strip()
        elif current_section == 'body':
            body += '\n' + line
    
    # Fallback if parsing fails
    if not subject:
        subject = "Notification"
    if not body:
        body = llm_response
    
    activity.logger.info("Generated email — subject=%r", subject)
    
    # Prepare email data
    email_data = {
        "to": input.to,
        "subject": subject.strip(),
        "body": body.strip(),
        "from_email": input.from_email,
        "from_name": input.from_name,
        "reply_to": input.reply_to,
        "cc": input.cc,
        "bcc": input.bcc,
    }
    
    # Remove None values
    email_data = {k: v for k, v in email_data.items() if v is not None}
    
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
