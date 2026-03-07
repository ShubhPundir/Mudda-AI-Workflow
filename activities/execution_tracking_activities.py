"""
Execution tracking activities for updating workflow execution status.

Moved from the old monolithic WorkflowActivities class.
Uses async DB sessions properly.
"""
import logging
import os
from datetime import datetime
from temporalio import activity
from sqlalchemy import update
from schemas.activity_schemas import UpdateExecutionStatusInput, UpdateExecutionStatusOutput
import httpx

logger = logging.getLogger(__name__)


@activity.defn
async def update_execution_status(input: UpdateExecutionStatusInput) -> UpdateExecutionStatusOutput:
    """
    Update workflow execution status in the database AND emit SSE events.

    Args:
        input: UpdateExecutionStatusInput containing execution_id, status, and optional result_data/event_type.

    Returns:
        UpdateExecutionStatusOutput confirming the status update.
    """
    logger.info(
        "Updating execution status — execution_id=%s status=%s event=%s",
        input.execution_id,
        input.status,
        input.event_type
    )

    from sessions.database import AsyncSessionLocal
    from models import WorkflowExecution

    # 1. Update Database
    async with AsyncSessionLocal() as db:
        try:
            stmt = (
                update(WorkflowExecution)
                .where(WorkflowExecution.id == input.execution_id)
                .values(status=input.status)
            )
            if input.result_data is not None:
                stmt = stmt.values(execution_data=input.result_data)
            
            # If completed, set completed_at
            if input.status in ['completed', 'failed']:
                stmt = stmt.values(completed_at=datetime.utcnow())

            await db.execute(stmt)
            await db.commit()
        except Exception as exc:
            await db.rollback()
            logger.error("Failed to update execution status in DB: %s", exc)
            # We continue to attempt event emission even if DB fail

    # 2. Emit SSE Event via internal bridge
    try:
        # Default to 8081 as seen in the user's terminal/main.py
        api_url = os.getenv("API_URL", "http://localhost:8081")
        event_type = input.event_type or f"execution_{input.status}"
        
        event_data = {
            "status": input.status,
            "step_id": input.step_id,
            "step_name": input.step_name,
            "timestamp": datetime.utcnow().isoformat()
        }
        if input.result_data:
            event_data["result"] = input.result_data

        async with httpx.AsyncClient() as client:
            await client.post(
                f"{api_url}/workflow-executions/internal/event",
                json={
                    "execution_id": input.execution_id,
                    "event_type": event_type,
                    "data": event_data
                },
                timeout=2.0
            )
    except Exception as exc:
        logger.error("Failed to emit SSE event for execution_id=%s: %s", input.execution_id, str(exc), exc_info=True)

    return UpdateExecutionStatusOutput(
        execution_id=input.execution_id,
        status=input.status,
        updated=True,
    )
