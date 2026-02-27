"""
Issue update activities.

Handles database updates related to civic issue tracking.
Uses async DB sessions safely.
"""
import logging
from typing import Any, Dict
from temporalio import activity
from services.issue_service import fetch_issue_details, update_issue

logger = logging.getLogger(__name__)


@activity.defn
async def update_issue_activity(input: Dict[str, Any]) -> Dict[str, Any]:
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

    logger.info(
        "update_issue_activity — step_id=%s issue_id=%s",
        step_id,
        issue_id,
    )

    if not issue_id:
        raise ValueError("issue_id is required for update_issue activity")

    try:
        # Prepare fields to update
        update_fields = {
            k: v
            for k, v in input.items()
            if k not in ("step_id", "issue_id") and v is not None
        }

        # Call service to perform update
        result = await update_issue(issue_id, update_fields)
        
        return {
            "step_id": step_id,
            "issue_id": issue_id,
            "status": "completed",
            "service_result": result,
            "updated_fields": update_fields
        }
    except Exception as exc:
        logger.error("Failed to update issue: %s", exc, exc_info=True)
        raise



@activity.defn
async def fetch_issue_details_activity(input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch details for a specific issue from the API.

    Args:
        input: Dict containing:
            - issue_id (str): ID of the issue to fetch.
            - step_id (str, optional): Originating workflow step ID.

    Returns:
        Structured JSON with issue details.
    """
    step_id = input.get("step_id", "unknown")
    issue_id = input.get("issue_id")

    logger.info(
        "fetch_issue_details_activity — step_id=%s issue_id=%s",
        step_id,
        issue_id,
    )

    if not issue_id:
        raise ValueError("issue_id is required for fetch_issue_details activity")

    try:
        details = await fetch_issue_details(issue_id)
        return {
            "step_id": step_id,
            "issue_id": issue_id,
            "status": "completed",
            "details": details
        }
    except Exception as exc:
        logger.error("Failed to fetch issue details: %s", exc, exc_info=True)
        raise
