"""
Router for streaming workflow generation using Server-Sent Events (SSE)
"""
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator, Dict, Any

from sessions.database import get_db
from services.ai_service import ai_service
from services.workflow_service import WorkflowService
from schemas import IssueDetailsRequest
from models import WorkflowPlan
from datetime import datetime


router = APIRouter(prefix="/workflows", tags=["workflows"])


async def generate_sse_stream(db: AsyncSession, issue_details: Dict[str, Any]) -> AsyncGenerator[str, None]:
    """
    Generate Server-Sent Events stream for workflow generation progress.
    
    Args:
        db: Database session
        issue_details: Structured issue details dictionary
        
    Yields:
        SSE-formatted strings
    """
    workflow_json = None
    rag_service_unavailable = False
    
    try:
        # Check RAG service availability before starting
        from infrastructure.rag import get_rag_client
        rag_client = get_rag_client()
        
        if rag_client is None:
            rag_service_unavailable = True
            # Send warning event about RAG service
            warning_data = {
                "message": "RAG service is unavailable - workflow will be generated without policy context",
                "service": "rag",
                "severity": "warning",
                "impact": "Policy retrieval will be skipped"
            }
            yield f"event: service_warning\n"
            yield f"data: {json.dumps(warning_data)}\n\n"
        
        # Stream progress events from AI service
        async for event in ai_service.generate_workflow_plan_stream(issue_details=issue_details):
            event_type = event.get("event", "message")
            event_data = event.get("data", {})
            
            # Check if policy retrieval failed and send additional warning
            if event_type == "policy_retrieval_complete":
                if not event_data.get("rag_available", True):
                    # Send explicit warning event
                    warning_data = {
                        "message": event_data.get("warning", "Policy retrieval failed"),
                        "service": "rag",
                        "severity": "warning",
                        "impact": "Workflow generated without policy compliance context",
                        "policies_retrieved": len(event_data.get("policies", []))
                    }
                    yield f"event: service_warning\n"
                    yield f"data: {json.dumps(warning_data)}\n\n"
            
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
                issue_id=str(issue_details.get("issue_id")),  # Link to issue
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
                "created_at": workflow_plan.created_at.isoformat() if workflow_plan.created_at else datetime.utcnow().isoformat(),
                "rag_service_available": not rag_service_unavailable,
                "issue_id": issue_details.get("issue_id")
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
    request: IssueDetailsRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a workflow plan with streaming progress updates via SSE.
    
    Args:
        request: Structured issue details request
        db: Database session
        
    Returns:
        StreamingResponse with SSE events
        
    Example:
        {
            "issue_id": 1709812200000,
            "issue_category": "INFRASTRUCTURE",
            "created_at": "2024-03-07T10:30:00.000Z",
            "description": "Major water pipe burst causing severe flooding",
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
            "media_urls": [],
            "title": "Emergency: Water Pipe Burst"
        }
    """
    # Convert request to dict for streaming
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
    
    return StreamingResponse(
        generate_sse_stream(db, issue_details),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )

