"""
Pydantic schemas for Temporal activity inputs and outputs.

These schemas provide type safety, validation, and documentation for all
activity parameters across the workflow system.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Document Activities
# ============================================================================

class PDFServiceInput(BaseModel):
    """Input schema for pdf_service_activity."""
    step_id: Optional[str] = Field(default="unknown", description="Workflow step identifier")
    problem_statement: str = Field(..., description="Problem statement for report generation")
    title: Optional[str] = Field(None, description="Report title")
    report_type: Optional[str] = Field(default="summary", description="Type of report to generate")
    
    class Config:
        json_schema_extra = {
            "example": {
                "step_id": "step_001",
                "problem_statement": "Water leak at Main Street",
                "title": "Water Leak Investigation Report",
                "report_type": "summary"
            }
        }


class PDFServiceOutput(BaseModel):
    """Output schema for pdf_service_activity."""
    step_id: str = Field(..., description="Workflow step identifier")
    status: str = Field(..., description="Activity completion status")
    file_path: str = Field(..., description="Local file path of generated PDF")
    s3_url: str = Field(..., description="S3 URL of uploaded PDF")
    filename: str = Field(..., description="Generated filename")
    size_bytes: int = Field(..., description="File size in bytes")
    ai_metadata: Dict[str, Any] = Field(..., description="AI generation metadata")


# ============================================================================
# Execution Tracking Activities
# ============================================================================

class UpdateExecutionStatusInput(BaseModel):
    """Input schema for update_execution_status activity."""
    execution_id: str = Field(..., description="Workflow execution ID")
    status: str = Field(..., description="New execution status")
    result_data: Optional[Dict[str, Any]] = Field(None, description="Optional result or error data")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status is one of the allowed values."""
        allowed = ['pending', 'running', 'completed', 'failed']
        if v not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "execution_id": "exec_123",
                "status": "completed",
                "result_data": {"steps_completed": 5}
            }
        }


class UpdateExecutionStatusOutput(BaseModel):
    """Output schema for update_execution_status activity."""
    execution_id: str = Field(..., description="Workflow execution ID")
    status: str = Field(..., description="Updated status")
    updated: bool = Field(..., description="Whether update was successful")


# ============================================================================
# External Service Activities
# ============================================================================


# ============================================================================
# Worker / Dispatch Activities
# ============================================================================

class DispatchWorkerInput(BaseModel):
    """Input schema for dispatch_worker_activity."""
    step_id: Optional[str] = Field(default="unknown", description="Workflow step identifier")
    worker_type: str = Field(..., description="Type of worker to dispatch (e.g., plumber, electrician)")
    issue_id: str = Field(..., description="Related civic issue ID")
    location: str = Field(..., description="Location to dispatch the worker to")
    urgency: str = Field(default="normal", description="Urgency of the dispatch")
    description: str = Field(..., description="Description of the task")

    class Config:
        json_schema_extra = {
            "example": {
                "step_id": "step_001_dispatch",
                "worker_type": "plumber",
                "issue_id": "ISSUE-2024-00187",
                "location": "42 MG Road, Sector 14, Gurugram",
                "urgency": "critical",
                "description": "Major water pipe burst"
            }
        }


class DispatchWorkerOutput(BaseModel):
    """Output schema for dispatch_worker_activity."""
    step_id: str = Field(..., description="Workflow step identifier")
    status: str = Field(..., description="Activity completion status")
    dispatch_id: str = Field(..., description="Unique ID for the dispatch record")
    worker_notified: bool = Field(..., description="Whether a worker was successfully notified")
    message: str = Field(..., description="Status message")


class RequestSitePhotosInput(BaseModel):
    """Input schema for request_site_photos_activity."""
    step_id: Optional[str] = Field(default="unknown", description="Workflow step identifier")
    dispatch_id: str = Field(..., description="ID of the previously created dispatch")
    message: str = Field(default="Please upload photos of the site before and after the repair.", description="Instructions for the worker")

    class Config:
        json_schema_extra = {
            "example": {
                "step_id": "step_002_photos",
                "dispatch_id": "disp_8901",
                "message": "Upload high-res photos of the broken pipe."
            }
        }


class RequestSitePhotosOutput(BaseModel):
    """Output schema for request_site_photos_activity."""
    step_id: str = Field(..., description="Workflow step identifier")
    status: str = Field(..., description="Activity completion status")
    request_id: str = Field(..., description="Unique ID for the photo request")


class ConfirmTaskCompletionInput(BaseModel):
    """Input schema for confirm_task_completion_activity."""
    step_id: Optional[str] = Field(default="unknown", description="Workflow step identifier")
    dispatch_id: str = Field(..., description="ID of the dispatch being completed")
    notes: Optional[str] = Field(None, description="Any closing notes from the internal system")

    class Config:
        json_schema_extra = {
            "example": {
                "step_id": "step_003_confirm",
                "dispatch_id": "disp_8901",
                "notes": "Worker uploaded photos and marked as done."
            }
        }


class ConfirmTaskCompletionOutput(BaseModel):
    """Output schema for confirm_task_completion_activity."""
    step_id: str = Field(..., description="Workflow step identifier")
    status: str = Field(..., description="Activity completion status")
    confirmed_at: str = Field(..., description="Timestamp of confirmation")



# ============================================================================
# Human Activities
# ============================================================================



# ============================================================================
# Issue Activities
# ============================================================================

class UpdateIssueInput(BaseModel):
    """Input schema for update_issue_activity."""
    issue_id: str = Field(..., description="Civic issue ID to update")
    status: str = Field(..., description="New issue status")
    step_id: Optional[str] = Field(default="unknown", description="Workflow step identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "issue_id": "issue_789",
                "status": "in_progress",
                "step_id": "step_004"
            }
        }


class UpdateIssueOutput(BaseModel):
    """Output schema for update_issue_activity."""
    step_id: str = Field(..., description="Workflow step identifier")
    issue_id: str = Field(..., description="Updated issue ID")
    status: str = Field(..., description="Activity completion status")
    service_result: Dict[str, Any] = Field(..., description="Service layer result")


class FetchIssueDetailsInput(BaseModel):
    """Input schema for fetch_issue_details_activity."""
    issue_id: str = Field(..., description="Civic issue ID to fetch")
    step_id: Optional[str] = Field(default="unknown", description="Workflow step identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "issue_id": "issue_789",
                "step_id": "step_005"
            }
        }


class FetchIssueDetailsOutput(BaseModel):
    """Output schema for fetch_issue_details_activity."""
    step_id: str = Field(..., description="Workflow step identifier")
    issue_id: str = Field(..., description="Fetched issue ID")
    status: str = Field(..., description="Activity completion status")
    details: Dict[str, Any] = Field(..., description="Issue details")




# ============================================================================
# Notification Activities
# ============================================================================

class SendNotificationInput(BaseModel):
    """Input schema for send_notification activity."""
    to: List[str] | str = Field(..., description="Recipient email address(es)")
    content: str = Field(..., description="Description of what the email should communicate. LLM will generate subject and body from this.")
    from_email: Optional[str] = Field(None, description="Sender email address")
    from_name: Optional[str] = Field(None, description="Sender display name")
    reply_to: Optional[str] = Field(None, description="Reply-to address")
    cc: Optional[List[str]] = Field(None, description="CC recipients")
    bcc: Optional[List[str]] = Field(None, description="BCC recipients")
    step_id: Optional[str] = Field(default="unknown", description="Workflow step identifier")
    issue_id: Optional[str] = Field(default="unknown", description="Related civic issue ID")
    
    @field_validator('to')
    @classmethod
    def validate_to(cls, v: List[str] | str) -> List[str]:
        """Ensure 'to' is always a list."""
        if isinstance(v, str):
            return [v]
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "to": ["official@city.gov"],
                "content": "Notify the official that the water leak repair has been completed. Include the report URL from the previous step.",
                "step_id": "step_008",
                "issue_id": "issue_123"
            }
        }


class SendNotificationOutput(BaseModel):
    """Output schema for send_notification activity."""
    step_id: str = Field(..., description="Workflow step identifier")
    status: str = Field(..., description="Activity completion status")
    channel: str = Field(..., description="Notification channel used")
    message_id: str = Field(..., description="Email service message ID")
    to: List[str] = Field(..., description="Recipient addresses")
    subject: str = Field(..., description="Email subject")
