"""
Issue update activities.

Handles database updates related to civic issue tracking.
Uses async DB sessions safely.
"""
import logging
from temporalio import activity
from services.issue_service import fetch_issue_details, update_issue
from schemas.activity_schemas import (
    UpdateIssueInput,
    UpdateIssueOutput,
    FetchIssueDetailsInput,
    FetchIssueDetailsOutput,
)

logger = logging.getLogger(__name__)


@activity.defn
async def update_issue_activity(input: UpdateIssueInput) -> UpdateIssueOutput:
    """
    Update a civic issue record's status in the database.

    Args:
        input: UpdateIssueInput containing issue_id, status, and step_id.

    Returns:
        UpdateIssueOutput confirming the update.
    """
    logger.info(
        "update_issue_activity — step_id=%s issue_id=%s",
        input.step_id,
        input.issue_id,
    )

    try:
        # Call service to perform update
        result = await update_issue(input.issue_id, input.status)
        
        return UpdateIssueOutput(
            step_id=input.step_id,
            issue_id=input.issue_id,
            status="completed",
            service_result=result
        )
    except Exception as exc:
        logger.error("Failed to update issue: %s", exc, exc_info=True)
        raise



@activity.defn
async def fetch_issue_details_activity(input: FetchIssueDetailsInput) -> FetchIssueDetailsOutput:
    """
    Fetch details for a specific issue from the API.

    Args:
        input: FetchIssueDetailsInput containing issue_id and step_id.

    Returns:
        FetchIssueDetailsOutput with issue details.
    """
    logger.info(
        "fetch_issue_details_activity — step_id=%s issue_id=%s",
        input.step_id,
        input.issue_id,
    )

    try:
        details = await fetch_issue_details(input.issue_id)
        return FetchIssueDetailsOutput(
            step_id=input.step_id,
            issue_id=input.issue_id,
            status="completed",
            details=details
        )
    except Exception as exc:
        logger.error("Failed to fetch issue details: %s", exc, exc_info=True)
        raise
