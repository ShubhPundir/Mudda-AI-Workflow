import logging
from typing import Any, Dict, Optional
from sqlalchemy.future import select
from sqlalchemy import update as sa_update
from sessions.database import AsyncSessionLocal
from models.issue import Issue, IssueStatus

logger = logging.getLogger(__name__)

# TODO: change the code to something cleaner

async def fetch_issue_details(issue_id: str) -> Dict[str, Any]:
    """
    Fetch issue details from the database.
    
    Args:
        issue_id: The unique identifier for the issue.
        
    Returns:
        A dictionary containing issue details.
    """
    logger.info(f"Fetching issue details for issue_id: {issue_id}")
    
    async with AsyncSessionLocal() as db:
        try:
            # Convert string ID to int
            stmt = select(Issue).where(Issue.id == int(issue_id))
            result = await db.execute(stmt)
            issue = result.scalars().first()
            
            if not issue:
                logger.error(f"Issue with ID {issue_id} not found")
                raise ValueError(f"Issue {issue_id} not found")
            
            # Map model to dictionary
            return {
                "id": str(issue.id),
                "title": issue.title,
                "description": issue.description,
                "status": issue.status.value if hasattr(issue.status, 'value') else str(issue.status),
                "user_id": str(issue.user_id),
                "location_id": str(issue.location_id),
                "category_id": str(issue.category_id),
                "media_urls": issue.media_urls or [],
                "urgency_flag": issue.urgency_flag,
                "severity_score": issue.severity_score,
                "created_at": issue.created_at.isoformat() if issue.created_at else None,
                "updated_at": issue.updated_at.isoformat() if issue.updated_at else None
            }
        except Exception as e:
            logger.error(f"Error fetching issue {issue_id}: {e}")
            raise

async def update_issue(issue_id: str, status: str) -> Dict[str, Any]:
    """
    Update a civic issue record's status in the database.
    
    Args:
        issue_id: ID of the issue to update.
        status: String representing the new status (e.g., "IN_PROGRESS").
        
    Returns:
        A dictionary confirming the update.
    """
    logger.info(f"Updating issue {issue_id} status to: {status}")
    
    try:
        status_enum = IssueStatus(status.upper())
    except ValueError:
        logger.error(f"Invalid status: {status}")
        raise ValueError(f"Invalid status: {status}, must be one of {IssueStatus}")

    async with AsyncSessionLocal() as db:
        try:
            stmt = (
                sa_update(Issue)
                .where(Issue.id == int(issue_id))
                .values(status=status_enum)
            )

            result = await db.execute(stmt)
            if result.rowcount == 0:
                logger.error(f"Issue with ID {issue_id} not found")
                await db.rollback()
                raise ValueError(f"Issue {issue_id} not found")
            await db.commit()
            
            return {
                "issue_id": issue_id,
                "status": status_enum.value,
                "updated_fields": ["status"]
            }
        except Exception as exc:
            await db.rollback()
            logger.error(f"Failed to update issue {issue_id}: {exc}")
            raise
