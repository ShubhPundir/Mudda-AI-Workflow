"""
Pydantic schemas for AI service structured outputs
Zero regex, hard schema validation at decode time
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator


class ActivitySelectionResponse(BaseModel):
    """Schema for activity selection output"""
    selected_activity_ids: List[str] = Field(
        ...,
        description="List of selected activity IDs relevant to the problem",
        min_length=1
    )


class WorkflowStep(BaseModel):
    """Schema for a single workflow step"""
    step_id: str = Field(..., description="Unique identifier for this step")
    activity_id: str = Field(..., description="ID of the activity to execute")
    description: str = Field(..., description="Human-readable description of what this step does")
    inputs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Input parameters for the activity (can use templates like {{variable}})"
    )
    outputs: List[str] = Field(
        default_factory=list,
        description="List of output variable names this step produces"
    )
    next: List[str] = Field(
        default_factory=list,
        description="List of next step IDs to execute (empty for terminal steps)"
    )

    @field_validator('step_id', 'activity_id', 'description')
    @classmethod
    def validate_non_empty_strings(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class WorkflowPlanResponse(BaseModel):
    """Schema for workflow plan generation output"""
    workflow_name: str = Field(..., description="Short, descriptive name for the workflow")
    description: str = Field(..., description="Detailed description of what the workflow accomplishes")
    steps: List[WorkflowStep] = Field(
        ...,
        description="Ordered list of workflow steps forming a DAG",
        min_length=1
    )

    @field_validator('workflow_name', 'description')
    @classmethod
    def validate_non_empty_strings(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()

    @field_validator('steps')
    @classmethod
    def validate_dag_structure(cls, steps):
        """Validate that steps form a valid DAG (no cycles)"""
        if not steps:
            raise ValueError("Workflow must have at least one step")
        
        step_ids = {step.step_id for step in steps}
        
        # Validate all referenced next steps exist
        for step in steps:
            for next_id in step.next:
                if next_id not in step_ids:
                    raise ValueError(f"Step '{step.step_id}' references non-existent step '{next_id}'")
        
        # Basic cycle detection using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(step_id: str, adjacency: Dict[str, List[str]]) -> bool:
            visited.add(step_id)
            rec_stack.add(step_id)
            
            for neighbor in adjacency.get(step_id, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, adjacency):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(step_id)
            return False
        
        # Build adjacency list
        adjacency = {step.step_id: step.next for step in steps}
        
        # Check for cycles starting from each node
        for step in steps:
            if step.step_id not in visited:
                if has_cycle(step.step_id, adjacency):
                    raise ValueError("Workflow contains cycles - must be a DAG")
        
        return steps

    def validate_activity_ids(self, valid_activity_ids: set) -> None:
        """Validate that all activity_ids exist in the registry"""
        for step in self.steps:
            if step.activity_id not in valid_activity_ids:
                raise ValueError(
                    f"Step '{step.step_id}' references non-existent activity '{step.activity_id}'"
                )
