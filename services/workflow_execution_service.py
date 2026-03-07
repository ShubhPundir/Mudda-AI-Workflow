"""
Service layer for Workflow Execution operations
"""
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import WorkflowPlan, WorkflowExecution
from schemas import WorkflowExecutionResponse
from datetime import datetime
from temporal.client import temporal_client_manager

class WorkflowExecutionService:
    """Service class for Workflow Execution operations"""
    
    @staticmethod
    async def execute_workflow(db: AsyncSession, workflow_plan_id: str, execution_data: Optional[Dict[str, Any]] = None) -> WorkflowExecutionResponse:
        """
        Execute a workflow plan via Temporal
        
        Args:
            db: Database session
            workflow_plan_id: UUID of the workflow plan to execute
            execution_data: Optional execution parameters
            
        Returns:
            Execution details with Temporal workflow ID
        """
        # Verify workflow exists and get the plan
        result = await db.execute(select(WorkflowPlan).filter(WorkflowPlan.id == workflow_plan_id))
        workflow = result.scalars().first()
        if not workflow:
            raise ValueError("Workflow plan not found")
        
        # Create execution record first (to get UUID)
        execution = WorkflowExecution(
            workflow_plan_id=workflow_plan_id,
            execution_data=execution_data,
            status="pending"
        )
        
        db.add(execution)
        await db.commit()
        await db.refresh(execution)
        
        # Get the workflow plan JSON
        workflow_plan_json = workflow.plan_json
        if not workflow_plan_json:
            raise ValueError("Workflow plan has no steps defined")
        
        # Extract issue_details from execution_data if available
        issue_details = None
        if execution_data and isinstance(execution_data, dict):
            issue_details = execution_data.get("issue_details")
        
        try:
            # Connect to Temporal and start workflow
            temporal_workflow_id = await temporal_client_manager.execute_workflow(
                workflow_plan=workflow_plan_json,
                execution_id=str(execution.id),  # Pass execution UUID
                issue_details=issue_details  # Pass issue details for template resolution
            )
            
            # Update execution record with Temporal workflow ID
            execution.temporal_workflow_id = temporal_workflow_id
            execution.status = "running"
            execution.started_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(execution)
            
        except Exception as e:
            # Mark execution as failed if Temporal start fails
            execution.status = "failed"
            execution.execution_data = {
                "error": str(e),
                "error_type": "temporal_start_failed"
            }
            await db.commit()
            raise ValueError(f"Failed to start Temporal workflow: {str(e)}")
        
        return WorkflowExecutionResponse(
            execution_id=str(execution.id),
            workflow_plan_id=str(execution.workflow_plan_id),
            temporal_workflow_id=execution.temporal_workflow_id,
            status=execution.status,
            started_at=execution.started_at,
            created_at=execution.created_at or datetime.utcnow()
        )
    
    @staticmethod
    async def get_execution(db: AsyncSession, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get workflow execution details
        
        Args:
            db: Database session
            execution_id: UUID of the execution
            
        Returns:
            Execution details or None if not found
        """
        result = await db.execute(select(WorkflowExecution).filter(WorkflowExecution.id == execution_id))
        execution = result.scalars().first()
        
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
