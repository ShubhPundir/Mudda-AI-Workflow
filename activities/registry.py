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
    "pdf_service_activity": {
        "id": "pdf_service_activity",
        "name": "Generate PDF Report",
        "description": "Generates a PDF report using AI content and local templates, then uploads to S3 for secure access and distribution.",
        "inputs": ["content", "template_id"],
        "outputs": ["s3_url", "file_path", "filename"],
        "schema": {
            "inputs": {
                "step_id": "string (required)",
                "content": "string (required) - Data to include in report",
                "title": "string (optional) - Custom title for report",
                "report_type": "string (optional) - Type of report (default: summary)"
            }
        },
        "example": {
            "step_id": "step_002_generate_report",
            "activity_id": "pdf_service_activity",
            "description": "Generate damage assessment report",
            "requires_approval": False,
            "inputs": {
                "step_id": "step_002_generate_report",
                "content": "Water leak investigation at {{step_001_fetch_issue.location}}. Damage: {{step_001_fetch_issue.description}}",
                "title": "Water Leak Investigation Report",
                "report_type": "damage_assessment"
            }
        }
    },
    "update_issue_activity": {
        "id": "update_issue_activity",
        "name": "Update Issue Status",
        "description": "Synchronizes the current workflow state with the main database issue record using LLM-enhanced status summaries and next-step recommendations.",
        "inputs": ["issue_id", "status", "notes"],
        "outputs": ["success", "llm_summary", "next_step_recommendation"],
        "schema": {
            "inputs": {
                "step_id": "string (required)",
                "issue_id": "string (required) - ID of the issue to update",
                "status": "string (required) - New status (e.g., 'resolved', 'in_progress')",
                "notes": "string (optional) - Details about the update"
            }
        },
        "example": {
            "step_id": "step_004_update_status",
            "activity_id": "update_issue_activity",
            "description": "Update issue status to in_progress",
            "requires_approval": False,
            "inputs": {
                "step_id": "step_004_update_status",
                "issue_id": "{{issue_id}}",
                "status": "in_progress",
                "notes": "Worker dispatched to site."
            }
        }
    },
    "dispatch_worker_activity": {
        "id": "dispatch_worker_activity",
        "name": "Dispatch Worker",
        "description": "Dispatches a worker (plumber, electrician, etc.) to a specific location to resolve an issue.",
        "inputs": ["worker_type", "issue_id", "location", "urgency", "description"],
        "outputs": ["dispatch_id", "status", "worker_notified", "worker_name", "worker_phone", "estimated_arrival", "worker_response", "message"],
        "schema": {
            "inputs": {
                "step_id": "string (required)",
                "issue_id": "string (required)",
                "worker_type": "string (required) - Type of worker (plumber, electrician, etc.)",
                "location": "string (required) - Where to dispatch",
                "urgency": "string (required) - low, high, critical",
                "description": "string (required) - Problem description for worker"
            }
        },
        "example": {
            "step_id": "step_001_dispatch",
            "activity_id": "dispatch_worker_activity",
            "description": "Dispatch plumber for water leak",
            "requires_approval": True,
            "inputs": {
                "step_id": "step_001_dispatch",
                "issue_id": "{{issue_id}}",
                "worker_type": "plumber",
                "location": "42 MG Road, Sector 14, Gurugram",
                "urgency": "critical",
                "description": "Major water pipe burst"
            }
        }
    },
    "request_site_photos_activity": {
        "id": "request_site_photos_activity",
        "name": "Request Site Photos",
        "description": "Requests photos from the dispatched worker for validation or record keeping.",
        "inputs": ["dispatch_id", "message"],
        "outputs": ["request_id", "status", "photos_uploaded", "photo_urls", "worker_notes"],
        "schema": {
            "inputs": {
                "step_id": "string (required)",
                "dispatch_id": "string (required) - ID from dispatch activity",
                "message": "string (required) - Instructions for what to photograph"
            }
        },
        "example": {
            "step_id": "step_002_photos",
            "activity_id": "request_site_photos_activity",
            "description": "Request before/after photos",
            "requires_approval": False,
            "inputs": {
                "step_id": "step_002_photos",
                "dispatch_id": "{{step_001_dispatch.dispatch_id}}",
                "message": "Upload photos of the broken pipe and the final fix."
            }
        }
    },
    "confirm_task_completion_activity": {
        "id": "confirm_task_completion_activity",
        "name": "Confirm Task Completion",
        "description": "Marks a worker dispatch task as fully completed in the system.",
        "inputs": ["dispatch_id", "notes"],
        "outputs": ["status", "confirmed_at", "completion_notes", "time_spent_minutes", "materials_used", "follow_up_required"],
        "schema": {
            "inputs": {
                "step_id": "string (required)",
                "dispatch_id": "string (required)",
                "notes": "string (optional) - Final completion notes"
            }
        },
        "example": {
            "step_id": "step_003_confirm",
            "activity_id": "confirm_task_completion_activity",
            "description": "Confirm plumbing job completion",
            "requires_approval": False,
            "inputs": {
                "step_id": "step_003_confirm",
                "dispatch_id": "{{step_001_dispatch.dispatch_id}}",
                "notes": "Work verified by inspector."
            }
        }
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
    from activities.worker_activities import (
        dispatch_worker_activity,
        request_site_photos_activity,
        confirm_task_completion_activity
    )
    
    
    return {
        "send_notification": send_notification,
        "pdf_service_activity": pdf_service_activity,
        "update_issue_activity": update_issue_activity,
        "fetch_issue_details_activity": fetch_issue_details_activity,
        "dispatch_worker_activity": dispatch_worker_activity,
        "request_site_photos_activity": request_site_photos_activity,
        "confirm_task_completion_activity": confirm_task_completion_activity,
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
