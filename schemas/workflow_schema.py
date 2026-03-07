"""
Pydantic schemas for Workflow models
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class WorkflowStepSchema(BaseModel):
    """Schema for individual workflow step"""
    step_id: str
    activity_id: str
    description: str
    inputs: Dict[str, Any]
    outputs: List[str]
    next: List[str]
    requires_approval: Optional[bool] = False


class WorkflowPlanSchema(BaseModel):
    """Schema for complete workflow plan"""
    workflow_name: str
    description: str
    steps: List[WorkflowStepSchema]


class Coordinate(BaseModel):
    """GPS coordinate schema"""
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")


class LocationDetails(BaseModel):
    """Location details schema"""
    address_line: str = Field(default="Not specified", description="Street address")
    city: str = Field(default="Not specified", description="City name")
    state: str = Field(default="Not specified", description="State name")
    pin_code: str = Field(default="000000", description="PIN/ZIP code")
    coordinate: Coordinate = Field(..., description="GPS coordinates with latitude and longitude")


class IssueDetailsRequest(BaseModel):
    """Request schema for workflow generation from issue details.
    
    This replaces the old problem_statement approach and provides
    structured context for better workflow generation.
    """
    issue_id: int = Field(..., description="Unique identifier for the issue (can be timestamp for manual generation)")
    issue_category: str = Field(..., description="Category of the issue (e.g., INFRASTRUCTURE, SANITATION, WATER)")
    created_at: str = Field(..., description="ISO 8601 timestamp when the issue was created")
    description: str = Field(..., description="Detailed description of the issue")
    location: LocationDetails = Field(..., description="Structured location information")
    media_urls: List[str] = Field(default_factory=list, description="URLs of photos/videos related to the issue")
    title: str = Field(..., description="Title/summary of the issue")

    class Config:
        json_schema_extra = {
            "example": {
                "issue_id": 1709812200000,
                "issue_category": "INFRASTRUCTURE",
                "created_at": "2024-03-07T10:30:00.000Z",
                "description": "Major water pipe burst causing severe flooding on MG Road",
                "location": {
                    "address_line": "42 MG Road, Sector 14",
                    "city": "Gurugram",
                    "state": "Haryana",
                    "pin_code": "122001",
                    "coordinate": {
                        "latitude": 28.4595,
                        "longitude": 77.0266
                    }
                },
                "media_urls": [
                    "https://example.com/photo1.jpg",
                    "https://example.com/photo2.jpg"
                ],
                "title": "Emergency: Water Pipe Burst"
            }
        }


# Legacy schema - kept for backward compatibility in other parts of the system
class ProblemStatementRequest(BaseModel):
    """Legacy request schema for workflow generation (deprecated)"""
    problem_statement: str = Field(..., description="Description of the civic issue to resolve")


class WorkflowGenerationResponse(BaseModel):
    """Response schema for workflow generation"""
    workflow_id: str
    workflow_plan: WorkflowPlanSchema
    status: str
    created_at: datetime


class WorkflowExecutionRequest(BaseModel):
    """Request schema for executing a workflow"""
    workflow_plan_id: Optional[str] = None
    execution_data: Optional[Dict[str, Any]] = None


class WorkflowExecutionResponse(BaseModel):
    """Response schema for workflow execution"""
    execution_id: str
    workflow_plan_id: str
    temporal_workflow_id: Optional[str] = None
    status: str
    started_at: Optional[datetime] = None
    created_at: datetime
