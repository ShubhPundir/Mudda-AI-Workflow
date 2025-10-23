"""
Service layer for Workflow operations
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from models import WorkflowPlan, WorkflowExecution
from schemas import (
    WorkflowPlanSchema, 
    WorkflowGenerationResponse, 
    WorkflowExecutionResponse,
    ProblemStatementRequest
)
from services.ai_service import AIService
from services.component_service import ComponentService
from datetime import datetime


class WorkflowService:
    """Service class for Workflow operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.component_service = ComponentService(db)
        self.ai_service = AIService(self.component_service)
    
    def generate_workflow(self, request: ProblemStatementRequest) -> WorkflowGenerationResponse:
        """
        Generate a workflow plan for a civic issue
        
        Args:
            request: Problem statement describing the civic issue
            
        Returns:
            Generated workflow plan with ID
        """
        try:
            # Generate the workflow plan using AI
            workflow_json = self.ai_service.generate_workflow_plan(request.problem_statement)
            
            # Save to database
            workflow_plan = WorkflowPlan(
                workflow_name=workflow_json["workflow_name"],
                description=workflow_json["description"],
                problem_statement=request.problem_statement,
                workflow_json=workflow_json,
                status="draft"
            )
            
            self.db.add(workflow_plan)
            self.db.commit()
            self.db.refresh(workflow_plan)
            
            return WorkflowGenerationResponse(
                workflow_id=str(workflow_plan.id),
                workflow_plan=WorkflowPlanSchema(**workflow_json),
                status=workflow_plan.status,
                created_at=workflow_plan.created_at or datetime.utcnow()
            )
            
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"Failed to generate workflow: {str(e)}")
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific workflow plan by ID
        
        Args:
            workflow_id: UUID of the workflow plan
            
        Returns:
            Workflow plan details or None if not found
        """
        workflow = self.db.query(WorkflowPlan).filter(WorkflowPlan.id == workflow_id).first()
        
        if not workflow:
            return None
        
        return {
            "id": str(workflow.id),
            "workflow_name": workflow.workflow_name,
            "description": workflow.description,
            "problem_statement": workflow.problem_statement,
            "workflow_json": workflow.workflow_json,
            "status": workflow.status,
            "created_at": workflow.created_at,
            "updated_at": workflow.updated_at
        }
    
    def list_workflows(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List all workflow plans
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of workflow plans
        """
        workflows = self.db.query(WorkflowPlan).offset(skip).limit(limit).all()
        
        return [
            {
                "id": str(workflow.id),
                "workflow_name": workflow.workflow_name,
                "description": workflow.description,
                "status": workflow.status,
                "created_at": workflow.created_at
            }
            for workflow in workflows
        ]
    
    def execute_workflow(self, workflow_id: str, execution_data: Optional[Dict[str, Any]] = None) -> WorkflowExecutionResponse:
        """
        Execute a workflow plan
        
        Args:
            workflow_id: UUID of the workflow plan to execute
            execution_data: Optional execution parameters
            
        Returns:
            Execution details
        """
        # Verify workflow exists
        workflow = self.db.query(WorkflowPlan).filter(WorkflowPlan.id == workflow_id).first()
        if not workflow:
            raise ValueError("Workflow plan not found")
        
        # Create execution record
        execution = WorkflowExecution(
            workflow_plan_id=workflow_id,
            execution_data=execution_data,
            status="pending"
        )
        
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        
        # TODO: Integrate with Temporal.io for actual execution
        # For now, just return the execution record
        
        return WorkflowExecutionResponse(
            execution_id=str(execution.id),
            workflow_plan_id=str(execution.workflow_plan_id),
            temporal_workflow_id=execution.temporal_workflow_id,
            status=execution.status,
            started_at=execution.started_at,
            created_at=execution.created_at or datetime.utcnow()
        )
    
    def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get workflow execution details
        
        Args:
            execution_id: UUID of the execution
            
        Returns:
            Execution details or None if not found
        """
        execution = self.db.query(WorkflowExecution).filter(WorkflowExecution.id == execution_id).first()
        
        if not execution:
            return None
        
        return {
            "id": str(execution.id),
            "workflow_plan_id": str(execution.workflow_plan_id),
            "temporal_workflow_id": execution.temporal_workflow_id,
            "status": execution.status,
            "execution_data": execution.execution_data,
            "started_at": execution.started_at,
            "completed_at": execution.completed_at,
            "created_at": execution.created_at
        }
