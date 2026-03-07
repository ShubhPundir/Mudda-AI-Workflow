"""
Workflow execution router
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from pydantic import BaseModel

from sessions.database import get_db
from services.workflow_execution_service import WorkflowExecutionService
from services.execution_event_bus import execution_event_bus
from schemas import (
    WorkflowExecutionRequest,
    WorkflowExecutionResponse
)

class InternalExecutionEvent(BaseModel):
    execution_id: str
    event_type: str
    data: Dict[str, Any]

router = APIRouter(prefix="/workflow-executions", tags=["workflow-executions"])

@router.post("/{workflow_plan_id}/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    workflow_plan_id: str,
    request: WorkflowExecutionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Execute a workflow plan
    
    Args:
        workflow_plan_id: UUID of the workflow plan to execute
        request: Execution parameters
        db: Database session
        
    Returns:
        Execution details
    """
    try:
        # Note: request.workflow_plan_id is in the body, but we use the path param
        return await WorkflowExecutionService.execute_workflow(db, workflow_plan_id, request.execution_data)
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


@router.get("/{execution_id}")
async def get_execution(
    execution_id: str,
    db: AsyncSession = Depends(get_db)
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
        execution = await WorkflowExecutionService.get_execution(db, execution_id)
        
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


@router.get("/{execution_id}/stream")
async def stream_execution_progress(
    execution_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Stream workflow execution progress via SSE.
    """
    # Verify execution exists
    execution = await WorkflowExecutionService.get_execution(db, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    return StreamingResponse(
        execution_event_bus.subscribe(execution_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/internal/event", include_in_schema=False)
async def push_internal_event(
    event: InternalExecutionEvent,
    request: Request
):
    """
    Internal endpoint for Temporal worker to push events to the API.
    In production, this should be protected by API key or IP whitelist.
    """
    await execution_event_bus.publish(
        event.execution_id,
        event.event_type,
        event.data
    )
    
    # If terminal event, close streams after a short delay
    if event.event_type in ["execution_completed", "execution_failed"]:
        import asyncio
        async def delayed_close():
            await asyncio.sleep(5)
            await execution_event_bus.close_stream(event.execution_id)
        
        asyncio.create_task(delayed_close())
        
    return {"status": "ok"}
