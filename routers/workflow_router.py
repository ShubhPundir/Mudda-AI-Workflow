"""
Workflow management router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from sessions.database import get_db
from services import WorkflowService
from schemas import (
    ProblemStatementRequest,
    WorkflowGenerationResponse,
    WorkflowExecutionRequest,
    WorkflowExecutionResponse
)

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("/generate", response_model=WorkflowGenerationResponse)
async def generate_workflow(
    request: ProblemStatementRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a workflow plan for a civic issue
    
    Args:
        request: Problem statement describing the civic issue
        db: Database session
        
    Returns:
        Generated workflow plan with ID
    """
    try:
        workflow_service = WorkflowService(db)
        return workflow_service.generate_workflow(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate workflow: {str(e)}"
        )


@router.get("/{workflow_id}")
async def get_workflow(
    workflow_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific workflow plan by ID
    
    Args:
        workflow_id: UUID of the workflow plan
        db: Database session
        
    Returns:
        Workflow plan details
    """
    try:
        workflow_service = WorkflowService(db)
        workflow = workflow_service.get_workflow(workflow_id)
        
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow plan not found"
            )
        
        return workflow
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow: {str(e)}"
        )


@router.get("")
async def list_workflows(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all workflow plans
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of workflow plans
    """
    try:
        workflow_service = WorkflowService(db)
        return workflow_service.list_workflows(skip, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list workflows: {str(e)}"
        )


@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    workflow_id: str,
    request: WorkflowExecutionRequest,
    db: Session = Depends(get_db)
):
    """
    Execute a workflow plan
    
    Args:
        workflow_id: UUID of the workflow plan to execute
        request: Execution parameters
        db: Database session
        
    Returns:
        Execution details
    """
    try:
        workflow_service = WorkflowService(db)
        return workflow_service.execute_workflow(workflow_id, request.execution_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute workflow: {str(e)}"
        )


@router.get("/executions/{execution_id}")
async def get_execution(
    execution_id: str,
    db: Session = Depends(get_db)
):
    """
    Get workflow execution details
    
    Args:
        execution_id: UUID of the execution
        db: Database session
        
    Returns:
        Execution details
    """
    try:
        workflow_service = WorkflowService(db)
        execution = workflow_service.get_execution(execution_id)
        
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Execution not found"
            )
        
        return execution
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get execution: {str(e)}"
        )
