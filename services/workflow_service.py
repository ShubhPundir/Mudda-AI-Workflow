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
    IssueDetailsRequest
)
from services.ai_service import ai_service
from datetime import datetime


class WorkflowService:
    """Service class for Workflow operations"""
    
    @staticmethod
    async def generate_workflow(
        db: AsyncSession, 
        request: IssueDetailsRequest
    ) -> WorkflowGenerationResponse:
        """
        Generate a workflow plan for a civic issue
        
        Args:
            db: Database session
            request: Structured issue details (IssueDetailsRequest)
            
        Returns:
            Generated workflow plan with ID
        """
        try:
            # Convert LocationDetails to dict for AI service
            location_dict = request.location.dict() if hasattr(request.location, 'dict') else request.location
            
            issue_details = {
                "issue_id": request.issue_id,
                "issue_category": request.issue_category,
                "created_at": request.created_at,
                "description": request.description,
                "location": location_dict,
                "media_urls": request.media_urls,
                "title": request.title
            }
            
            # Generate workflow using AI service
            workflow_json = await ai_service.generate_workflow_plan(issue_details=issue_details)
            issue_id = str(request.issue_id)  # Convert to string for database
            
            # Save to database
            workflow_plan = WorkflowPlan(
                name=workflow_json["workflow_name"],
                description=workflow_json["description"],
                issue_id=issue_id,  # Set from IssueDetailsRequest if provided
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
    
