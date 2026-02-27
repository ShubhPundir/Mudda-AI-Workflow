"""
Activity Registry & Metadata
Maps activity names (string) to the actual activity function and metadata.
This is used by BOTH the Temporal Worker for registration and the AI Service for plan generation.
"""
from typing import Any, Dict
from activities import (
    send_notification,
    contact_plumber,
    await_plumber_confirmation_activity,
    pdf_service_activity,
    update_issue_activity,
    fetch_issue_details_activity,
    llm_generate_dispatch_text_activity,
    generate_llm_content,
    human_feedback_activity,
    human_verification_activity,
)

ACTIVITY_METADATA: Dict[str, Dict[str, Any]] = {
    "send_notification": {
        "id": "send_notification",
        "name": "Send Notification",
        "description": "Sends an email notification via the infrastructure layer.",
        "inputs": ["recipient", "subject", "body"],
        "outputs": ["success"]
    },
    "contact_plumber": {
        "id": "contact_plumber",
        "name": "Contact Plumber",
        "description": "Initiates an automated API call to the plumber dispatch system.",
        "inputs": ["issue_id", "dispatch_text"],
        "outputs": ["booking_id", "estimated_arrival"]
    },
    "await_plumber_confirmation_activity": {
        "id": "await_plumber_confirmation_activity",
        "name": "Await Plumber Confirmation",
        "description": "Registers a wait state, expecting a manual signal from the plumber.",
        "inputs": ["booking_id"],
        "outputs": ["confirmation_status", "technician_notes"]
    },
    "pdf_service_activity": {
        "id": "pdf_service_activity",
        "name": "Generate PDF Report",
        "description": "Generates a PDF report using AI content and local templates, then uploads to S3.",
        "inputs": ["content", "template_id"],
        "outputs": ["report_url"]
    },
    "update_issue_activity": {
        "id": "update_issue_activity",
        "name": "Update Issue Status",
        "description": "Synchronizes the current workflow state with the main database issue record.",
        "inputs": ["issue_id", "status", "notes"],
        "outputs": ["success"]
    },
    "fetch_issue_details_activity": {
        "id": "fetch_issue_details_activity",
        "name": "Fetch Issue Details",
        "description": "Fetches external issue details from the API.",
        "inputs": ["issue_id"],
        "outputs": ["issue_details"]
    },
    "llm_generate_dispatch_text_activity": {
        "id": "llm_generate_dispatch_text_activity",
        "name": "Generate Dispatch Text",
        "description": "Uses LLM to generate highly contextualized dispatch instructions.",
        "inputs": ["issue_details"],
        "outputs": ["dispatch_text"]
    },
    "generate_llm_content": {
        "id": "generate_llm_content",
        "name": "Generate LLM Content",
        "description": "Generic AI content generation for reports and summaries.",
        "inputs": ["prompt", "context"],
        "outputs": ["content"]
    },
    "human_feedback_activity": {
        "id": "human_feedback_activity",
        "name": "Request Human Feedback",
        "description": "Pauses execution for a required approval/input from an official.",
        "inputs": ["message", "options"],
        "outputs": ["chosen_option", "comment"]
    },
    "human_verification_activity": {
        "id": "human_verification_activity",
        "name": "Human Work Verification",
        "description": "Specific human-in-the-loop verification for completed external work.",
        "inputs": ["work_id", "results"],
        "outputs": ["is_verified", "verification_notes"]
    },
}

# Mapping ID to actual callable for Temporal registration or direct execution (if needed)
ACTIVITY_REGISTRY: Dict[str, Any] = {
    "send_notification": send_notification,
    "contact_plumber": contact_plumber,
    "await_plumber_confirmation_activity": await_plumber_confirmation_activity,
    "pdf_service_activity": pdf_service_activity,
    "update_issue_activity": update_issue_activity,
    "fetch_issue_details_activity": fetch_issue_details_activity,
    "llm_generate_dispatch_text_activity": llm_generate_dispatch_text_activity,
    "generate_llm_content": generate_llm_content,
    "human_feedback_activity": human_feedback_activity,
    "human_verification_activity": human_verification_activity,
}
