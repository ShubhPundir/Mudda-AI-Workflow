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

class ContactPlumberInput(BaseModel):
    """Input schema for contact_plumber activity."""
    step_id: Optional[str] = Field(default="unknown", description="Workflow step identifier")
    issue_id: Optional[str] = Field(None, description="Related civic issue ID")
    location: Optional[str] = Field(None, description="Service location")
    description: Optional[str] = Field(None, description="Problem description")
    urgency: Optional[str] = Field(default="medium", description="Urgency level")
    
    @field_validator('urgency')
    @classmethod
    def validate_urgency(cls, v: Optional[str]) -> Optional[str]:
        """Validate urgency is one of the allowed values."""
        if v is not None:
            allowed = ['low', 'medium', 'high', 'critical']
            if v not in allowed:
                raise ValueError(f"Urgency must be one of {allowed}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "step_id": "step_002",
                "issue_id": "issue_456",
                "location": "123 Main St",
                "description": "Burst pipe in basement",
                "urgency": "high"
            }
        }


class ContactPlumberOutput(BaseModel):
    """Output schema for contact_plumber activity."""
    step_id: str = Field(..., description="Workflow step identifier")
    service: str = Field(..., description="Service type contacted")
    result: Dict[str, Any] = Field(..., description="Service response data")
    status: str = Field(..., description="Activity completion status")


class AwaitPlumberConfirmationInput(BaseModel):
    """Input schema for await_plumber_confirmation_activity."""
    step_id: Optional[str] = Field(default="unknown", description="Workflow step identifier")
    timeout_seconds: Optional[int] = Field(default=3600, description="Timeout for confirmation")


class AwaitPlumberConfirmationOutput(BaseModel):
    """Output schema for await_plumber_confirmation_activity."""
    status: str = Field(..., description="Waiting status")
    message: str = Field(..., description="Status message")


# ============================================================================
# Human Activities
# ============================================================================

class HumanFeedbackInput(BaseModel):
    """Input schema for human_feedback_activity."""
    step_id: Optional[str] = Field(default="unknown", description="Workflow step identifier")
    prompt: Optional[str] = Field(None, description="Feedback prompt for human")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for decision")
    
    class Config:
        json_schema_extra = {
            "example": {
                "step_id": "step_003",
                "prompt": "Approve emergency repair?",
                "context": {"cost": 5000, "urgency": "high"}
            }
        }


class HumanFeedbackOutput(BaseModel):
    """Output schema for human_feedback_activity."""
    approved: bool = Field(..., description="Whether action was approved")
    feedback: str = Field(..., description="Human feedback text")
    status: str = Field(..., description="Activity completion status")


class HumanVerificationInput(BaseModel):
    """Input schema for human_verification_activity."""
    step_id: Optional[str] = Field(default="unknown", description="Workflow step identifier")
    verification_type: Optional[str] = Field(default="quality", description="Type of verification needed")
    data_to_verify: Optional[Dict[str, Any]] = Field(None, description="Data requiring verification")


class HumanVerificationOutput(BaseModel):
    """Output schema for human_verification_activity."""
    verified: bool = Field(..., description="Whether verification passed")
    notes: str = Field(..., description="Verification notes")
    status: str = Field(..., description="Activity completion status")


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
# LLM Activities
# ============================================================================

class LLMGenerateDispatchTextInput(BaseModel):
    """Input schema for llm_generate_dispatch_text_activity."""
    description: str = Field(..., description="Problem description")
    category: Optional[str] = Field(default="General", description="Issue category")
    step_id: Optional[str] = Field(default="unknown", description="Workflow step identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "description": "Water main break on Oak Avenue",
                "category": "Water Emergency",
                "step_id": "step_006"
            }
        }


class LLMGenerateDispatchTextOutput(BaseModel):
    """Output schema for llm_generate_dispatch_text_activity."""
    dispatch_text: str = Field(..., description="Generated dispatch instructions")
    status: str = Field(..., description="Generation status")


class GenerateLLMContentInput(BaseModel):
    """Input schema for generate_llm_content activity."""
    problem_statement: str = Field(..., description="Problem statement for content generation")
    step_id: Optional[str] = Field(default="unknown", description="Workflow step identifier")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for generation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "problem_statement": "Generate summary of water infrastructure issues",
                "step_id": "step_007",
                "context": {"location": "Downtown", "timeframe": "last_month"}
            }
        }


class GenerateLLMContentOutput(BaseModel):
    """Output schema for generate_llm_content activity."""
    content: str = Field(..., description="Generated content")
    status: str = Field(..., description="Generation status")


# ============================================================================
# Notification Activities
# ============================================================================

class SendNotificationInput(BaseModel):
    """Input schema for send_notification activity."""
    to: List[str] | str = Field(..., description="Recipient email address(es)")
    subject: str = Field(..., description="Email subject")
    body: Optional[str] = Field(None, description="Plain-text email body")
    html: Optional[str] = Field(None, description="HTML email body")
    from_email: Optional[str] = Field(None, description="Sender email address")
    from_name: Optional[str] = Field(None, description="Sender display name")
    reply_to: Optional[str] = Field(None, description="Reply-to address")
    cc: Optional[List[str]] = Field(None, description="CC recipients")
    bcc: Optional[List[str]] = Field(None, description="BCC recipients")
    tags: Optional[List[Dict[str, str]]] = Field(None, description="Email metadata tags")
    attachments: Optional[List[Dict[str, Any]]] = Field(None, description="Email attachments")
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
                "subject": "Water Leak Report - Main Street",
                "body": "A water leak has been reported at Main Street.",
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
