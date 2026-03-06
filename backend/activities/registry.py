"""
Activity Registry & Metadata
Maps activity names (string) to the actual activity function and metadata.
This is used by BOTH the Temporal Worker for registration and the AI Service for plan generation.
"""
from typing import Any, Callable, Dict

ACTIVITY_METADATA: Dict[str, Dict[str, Any]] = {
    "send_notification": {
        "id": "send_notification",
        "name": "Send Notification",
        "description": "Sends an email notification with LLM-generated subject and body based on content description.",
        "inputs": ["to", "content"],
        "outputs": ["message_id", "status", "to", "subject"],
        "schema": {
            "inputs": {
                "step_id": "string (required)",
                "to": "string or list[string] (required) - Recipient email(s)",
                "content": "string (required) - What the email should communicate. LLM generates subject and body. Can use {{step_id.field}}",
                "issue_id": "string (optional)",
                "from_email": "string (optional)",
                "from_name": "string (optional)"
            }
        },
        "example": {
            "step_id": "step_003_notify",
            "activity_id": "send_notification",
            "description": "Notify official about completion",
            "requires_approval": False,
            "inputs": {
                "step_id": "step_003_notify",
                "to": "official@city.gov",
                "content": "Notify that repair at {{step_001_fetch_issue.location}} is complete. Report: {{step_002_generate_report.s3_url}}",
                "issue_id": "{{issue_id}}"
            }
        }
    },
    # TODO: add similar inputs, outputs, schemas, example for below
    "pdf_service_activity": {
        "id": "pdf_service_activity",
        "name": "Generate PDF Report",
        "description": "Generates a PDF report using AI content and local templates, then uploads to S3 with intelligent executive summary for downstream activities.",
        "inputs": ["content", "template_id"],
        "outputs": ["report_url", "executive_summary", "key_findings"]
    },
    "update_issue_activity": {
        "id": "update_issue_activity",
        "name": "Update Issue Status",
        "description": "Synchronizes the current workflow state with the main database issue record using LLM-enhanced status summaries and next-step recommendations.",
        "inputs": ["issue_id", "status", "notes"],
        "outputs": ["success", "llm_summary", "next_step_recommendation"]
    },
}

def _get_activity_registry() -> Dict[str, Callable]:
    """
    Lazy-load activity functions to avoid circular imports.
    This function is called when the registry is actually needed.
    NOTE: Import directly from modules to avoid circular dependency with __init__.py
    """
    from activities.notification_activities import send_notification
    
    from activities.document_activities import pdf_service_activity
    from activities.issue_activities import (
        update_issue_activity,
        fetch_issue_details_activity
    )
    
    
    return {
        "send_notification": send_notification,
        "pdf_service_activity": pdf_service_activity,
        "update_issue_activity": update_issue_activity,
        "fetch_issue_details_activity": fetch_issue_details_activity,
    }


# Lazy-loaded registry - call _get_activity_registry() when needed
_ACTIVITY_REGISTRY_CACHE: Dict[str, Callable] = {}


def get_activity_registry() -> Dict[str, Callable]:
    """Get the activity registry, loading it lazily on first access."""
    global _ACTIVITY_REGISTRY_CACHE
    if not _ACTIVITY_REGISTRY_CACHE:
        _ACTIVITY_REGISTRY_CACHE = _get_activity_registry()
    return _ACTIVITY_REGISTRY_CACHE


# For backward compatibility - this will be loaded lazily
class _ActivityRegistryProxy:
    """Proxy object that loads the registry on first access."""
    
    def __getitem__(self, key: str) -> Callable:
        return get_activity_registry()[key]
    
    def get(self, key: str, default: Any = None) -> Any:
        return get_activity_registry().get(key, default)
    
    def keys(self):
        return get_activity_registry().keys()
    
    def values(self):
        return get_activity_registry().values()
    
    def items(self):
        return get_activity_registry().items()
    
    def __contains__(self, key: str) -> bool:
        return key in get_activity_registry()
    
    def __iter__(self):
        return iter(get_activity_registry())


# Mapping ID to actual callable for Temporal registration or direct execution (if needed)
ACTIVITY_REGISTRY = _ActivityRegistryProxy()
