"""
Execution tracking activities for updating workflow execution status.

Moved from the old monolithic WorkflowActivities class.
Uses async DB sessions properly.
"""
import logging
from typing import Any, Dict, Optional
from temporalio import activity
from sqlalchemy import update

logger = logging.getLogger(__name__)


@activity.defn
async def update_execution_status(input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update workflow execution status in the database.

    Args:
        input: Dict containing:
            - execution_id (str): ID of the execution record.
            - status (str): New status (pending, running, completed, failed).
            - result_data (dict, optional): Optional result / error data.

    Returns:
        Dict confirming the status update.
    """
    execution_id: str = input["execution_id"]
    status: str = input["status"]
    result_data: Optional[Dict[str, Any]] = input.get("result_data")

    logger.info(
        "Updating execution status — execution_id=%s status=%s",
        execution_id,
        status,
    )

    from sessions.database import AsyncSessionLocal
    from models import WorkflowExecution

    async with AsyncSessionLocal() as db:
        try:
            stmt = (
                update(WorkflowExecution)
                .where(WorkflowExecution.id == execution_id)
                .values(status=status)
            )
            if result_data is not None:
                stmt = stmt.values(execution_data=result_data)

            await db.execute(stmt)
            await db.commit()

            logger.info(
                "Execution status updated — execution_id=%s status=%s",
                execution_id,
                status,
            )
        except Exception as exc:
            await db.rollback()
            logger.error(
                "Failed to update execution status: %s", exc, exc_info=True
            )
            raise

    return {
        "execution_id": execution_id,
        "status": status,
        "updated": True,
    }
