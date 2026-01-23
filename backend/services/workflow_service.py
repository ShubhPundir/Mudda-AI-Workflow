"""
Service layer for Workflow operations
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import WorkflowPlan, WorkflowExecution
from schemas import (
    WorkflowPlanSchema, 
    WorkflowGenerationResponse, 
    WorkflowExecutionResponse,
    ProblemStatementRequest
)
from services.ai_service import AIService
from datetime import datetime


class WorkflowService:
    """Service class for Workflow operations"""
    
    @staticmethod
    async def generate_workflow(db: AsyncSession, request: ProblemStatementRequest) -> WorkflowGenerationResponse:
        """
        Generate a workflow plan for a civic issue
        
        Args:
            db: Database session
            request: Problem statement describing the civic issue
            
        Returns:
            Generated workflow plan with ID
        """
        try:
            # Generate the workflow plan using AI
            workflow_json = await AIService.generate_workflow_plan(db, request.problem_statement)
            
            # Save to database
            workflow_plan = WorkflowPlan(
                name=workflow_json["workflow_name"],
                description=workflow_json["description"],
                issue_id=None,  # Can be set later when issue is created
                plan_json=workflow_json,
                ai_model_used="gemini-2.5-flash",
                status="DRAFT",
                version="1.0",
                is_temporal_ready=False
            )
            
            db.add(workflow_plan)
            await db.commit()
            await db.refresh(workflow_plan)
            
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
    
    @staticmethod
    async def update_workflow(db: AsyncSession, workflow_id: str, workflow_plan_schema: WorkflowPlanSchema) -> Optional[WorkflowGenerationResponse]:
        """
        Update an existing workflow plan
        
        Args:
            db: Database session
            workflow_id: UUID of the workflow plan
            workflow_plan_schema: New workflow plan data
            
        Returns:
            Updated workflow plan details or None if not found
        """
        result = await db.execute(select(WorkflowPlan).filter(WorkflowPlan.id == workflow_id))
        workflow = result.scalars().first()
        
        if not workflow:
            return None
            
        # Update the plan_json
        workflow.plan_json = workflow_plan_schema.model_dump()
        # Also update top-level fields if they changed
        workflow.name = workflow_plan_schema.workflow_name
        workflow.description = workflow_plan_schema.description
        
        await db.commit()
        await db.refresh(workflow)
        
        return WorkflowGenerationResponse(
            workflow_id=str(workflow.id),
            workflow_plan=workflow_plan_schema,
            status=workflow.status or "DRAFT",
            created_at=workflow.created_at or datetime.utcnow()
        )
    
    @staticmethod
    async def get_workflow(db: AsyncSession, workflow_id: str) -> Optional[WorkflowGenerationResponse]:
        """
        Get a specific workflow plan by ID
        
        Args:
            db: Database session
            workflow_id: UUID of the workflow plan
            
        Returns:
            Workflow plan details or None if not found
        """
        result = await db.execute(select(WorkflowPlan).filter(WorkflowPlan.id == workflow_id))
        workflow = result.scalars().first()
        
        if not workflow:
            return None
        
        # Parse the plan_json to create WorkflowPlanSchema
        plan_json = workflow.plan_json if workflow.plan_json else {}
        workflow_plan = WorkflowPlanSchema(**plan_json)
        
        return WorkflowGenerationResponse(
            workflow_id=str(workflow.id),
            workflow_plan=workflow_plan,
            status=workflow.status or "DRAFT",
            created_at=workflow.created_at or datetime.utcnow()
        )
    
    @staticmethod
    async def list_workflows(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[WorkflowGenerationResponse]:
        """
        List all workflow plans
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of workflow plans
        """
        result = await db.execute(select(WorkflowPlan).offset(skip).limit(limit))
        workflows = result.scalars().all()
        
        result = []
        for workflow in workflows:
            # Parse the plan_json to create WorkflowPlanSchema
            plan_json = workflow.plan_json if workflow.plan_json else {
                "workflow_name": workflow.name,
                "description": workflow.description,
                "steps": []
            }
            
            try:
                workflow_plan = WorkflowPlanSchema(**plan_json)
            except Exception:
                # Fallback if plan_json is malformed
                workflow_plan = WorkflowPlanSchema(
                    workflow_name=workflow.name,
                    description=workflow.description,
                    steps=[]
                )
            
            result.append(WorkflowGenerationResponse(
                workflow_id=str(workflow.id),
                workflow_plan=workflow_plan,
                status=workflow.status or "DRAFT",
                created_at=workflow.created_at or datetime.utcnow()
            ))
        
        return result
    
    @staticmethod
    async def execute_workflow(db: AsyncSession, workflow_id: str, execution_data: Optional[Dict[str, Any]] = None) -> WorkflowExecutionResponse:
        """
        Execute a workflow plan
        
        Args:
            db: Database session
            workflow_id: UUID of the workflow plan to execute
            execution_data: Optional execution parameters
            
        Returns:
            Execution details
        """
        # Verify workflow exists
        result = await db.execute(select(WorkflowPlan).filter(WorkflowPlan.id == workflow_id))
        workflow = result.scalars().first()
        if not workflow:
            raise ValueError("Workflow plan not found")
        
        # Create execution record
        execution = WorkflowExecution(
            workflow_plan_id=workflow_id,
            execution_data=execution_data,
            status="pending"
        )
        
        db.add(execution)
        await db.commit()
        await db.refresh(execution)
        
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
