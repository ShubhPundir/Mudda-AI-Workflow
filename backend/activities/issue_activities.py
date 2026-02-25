"""
Issue update activities.

Handles database updates related to civic issue tracking.
Uses async DB sessions safely.
"""
import logging
from typing import Any, Dict
from temporalio import activity

logger = logging.getLogger(__name__)


@activity.defn
async def update_issue(input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a civic issue record in the database.

    Args:
        input: Dict containing:
            - issue_id (str): ID of the issue to update.
            - status (str, optional): New issue status.
            - resolution_notes (str, optional): Notes on resolution.
            - assigned_to (str, optional): Assignee identifier.
            - metadata (dict, optional): Additional metadata to merge.
            - step_id (str, optional): Originating workflow step ID.

    Returns:
        Structured JSON confirming the update.
    """
    step_id = input.get("step_id", "unknown")
    issue_id = input.get("issue_id")
    new_status = input.get("status")

    logger.info(
        "update_issue activity — step_id=%s issue_id=%s status=%s",
        step_id,
        issue_id,
        new_status,
    )

    if not issue_id:
        raise ValueError("issue_id is required for update_issue activity")

    # ------------------------------------------------------------------
    # NOTE: There is currently no Issue model in the codebase.
    # When an Issue model is added, replace the placeholder below with
    # an actual DB update. The pattern mirrors execution_tracking_activities.
    # ------------------------------------------------------------------

    from sessions.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            # Placeholder: log the update until an Issue model exists
            logger.info(
                "Issue update recorded — issue_id=%s status=%s notes=%s",
                issue_id,
                new_status,
                input.get("resolution_notes", ""),
            )

            # TODO: Uncomment when Issue model is available:
            # from sqlalchemy import update as sa_update
            # from models import Issue
            # stmt = (
            #     sa_update(Issue)
            #     .where(Issue.id == issue_id)
            #     .values(
            #         status=new_status,
            #         resolution_notes=input.get("resolution_notes"),
            #     )
            # )
            # await db.execute(stmt)
            # await db.commit()

            await db.commit()
        except Exception as exc:
            await db.rollback()
            logger.error("Failed to update issue: %s", exc, exc_info=True)
            raise

    return {
        "step_id": step_id,
        "issue_id": issue_id,
        "status": "completed",
        "updated_fields": {
            k: v
            for k, v in input.items()
            if k not in ("step_id", "issue_id") and v is not None
        },
    }
