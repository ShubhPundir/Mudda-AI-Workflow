"""
Pydantic schemas for Workflow models
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class WorkflowStepSchema(BaseModel):
    """Schema for individual workflow step"""
    step_id: str
    component_id: str
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


class ProblemStatementRequest(BaseModel):
    """Request schema for workflow generation"""
    problem_statement: str = Field(..., description="Description of the civic issue to resolve")


class WorkflowGenerationResponse(BaseModel):
    """Response schema for workflow generation"""
    workflow_id: str
    workflow_plan: WorkflowPlanSchema
    status: str
    created_at: datetime


class WorkflowExecutionRequest(BaseModel):
    """Request schema for executing a workflow"""
    workflow_plan_id: str
    execution_data: Optional[Dict[str, Any]] = None


class WorkflowExecutionResponse(BaseModel):
    """Response schema for workflow execution"""
    execution_id: str
    workflow_plan_id: str
    temporal_workflow_id: Optional[str] = None
    status: str
    started_at: Optional[datetime] = None
    created_at: datetime
