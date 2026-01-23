"""
Router for streaming workflow generation using Server-Sent Events (SSE)
"""
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

from sessions.database import get_db
from services.ai_service import AIService
from services.workflow_service import WorkflowService
from schemas import ProblemStatementRequest
from models import WorkflowPlan
from datetime import datetime


router = APIRouter(prefix="/workflows", tags=["workflows"])


async def generate_sse_stream(db: AsyncSession, problem_statement: str) -> AsyncGenerator[str, None]:
    """
    Generate Server-Sent Events stream for workflow generation progress.
    
    Args:
        db: Database session
        problem_statement: Problem description
        
    Yields:
        SSE-formatted strings
    """
    workflow_json = None
    
    try:
        # Stream progress events from AI service
        async for event in AIService.generate_workflow_plan_stream(db, problem_statement):
            event_type = event.get("event", "message")
            event_data = event.get("data", {})
            
            # Store workflow JSON when generation completes
            if event_type == "workflow_generation_complete":
                workflow_json = event_data.get("workflow")
            
            # Format as SSE
            yield f"event: {event_type}\n"
            yield f"data: {json.dumps(event_data)}\n\n"
        
        # Save workflow to database if generation was successful
        if workflow_json:
            workflow_plan = WorkflowPlan(
                name=workflow_json["workflow_name"],
                description=workflow_json["description"],
                issue_id=None,
                plan_json=workflow_json,
                ai_model_used="gemini-2.5-flash",
                status="DRAFT",
                version="1.0",
                is_temporal_ready=False
            )
            
            db.add(workflow_plan)
            await db.commit()
            await db.refresh(workflow_plan)
            
            # Send final success event with workflow ID
            success_data = {
                "workflow_id": str(workflow_plan.id),
                "workflow_name": workflow_json["workflow_name"],
                "created_at": workflow_plan.created_at.isoformat() if workflow_plan.created_at else datetime.utcnow().isoformat()
            }
            yield f"event: workflow_saved\n"
            yield f"data: {json.dumps(success_data)}\n\n"
        
        # Send done event
        yield f"event: done\n"
        yield f"data: {json.dumps({'message': 'Stream complete'})}\n\n"
        
    except Exception as e:
        # Send error event
        error_data = {
            "message": str(e),
            "error": True
        }
        yield f"event: error\n"
        yield f"data: {json.dumps(error_data)}\n\n"


@router.post("/generate/stream")
async def generate_workflow_stream(
    request: ProblemStatementRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a workflow plan with streaming progress updates via SSE.
    
    Args:
        request: Problem statement request
        db: Database session
        
    Returns:
        StreamingResponse with SSE events
    """
    return StreamingResponse(
        generate_sse_stream(db, request.problem_statement),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )

