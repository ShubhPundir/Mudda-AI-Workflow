"""
Execution tracking activities for updating workflow execution status.

Moved from the old monolithic WorkflowActivities class.
Uses async DB sessions properly.
"""
import logging
from temporalio import activity
from sqlalchemy import update
from schemas.activity_schemas import UpdateExecutionStatusInput, UpdateExecutionStatusOutput

logger = logging.getLogger(__name__)


@activity.defn
async def update_execution_status(input: UpdateExecutionStatusInput) -> UpdateExecutionStatusOutput:
    """
    Update workflow execution status in the database.

    Args:
        input: UpdateExecutionStatusInput containing execution_id, status, and optional result_data.

    Returns:
        UpdateExecutionStatusOutput confirming the status update.
    """
    logger.info(
        "Updating execution status — execution_id=%s status=%s",
        input.execution_id,
        input.status,
    )

    from sessions.database import AsyncSessionLocal
    from models import WorkflowExecution

    async with AsyncSessionLocal() as db:
        try:
            stmt = (
                update(WorkflowExecution)
                .where(WorkflowExecution.id == input.execution_id)
                .values(status=input.status)
            )
            if input.result_data is not None:
                stmt = stmt.values(execution_data=input.result_data)

            await db.execute(stmt)
            await db.commit()

            logger.info(
                "Execution status updated — execution_id=%s status=%s",
                input.execution_id,
                input.status,
            )
        except Exception as exc:
            await db.rollback()
            logger.error(
                "Failed to update execution status: %s", exc, exc_info=True
            )
            raise

    return UpdateExecutionStatusOutput(
        execution_id=input.execution_id,
        status=input.status,
        updated=True,
    )
