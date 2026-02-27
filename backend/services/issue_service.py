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

async def update_issue(issue_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a civic issue record in the database.
    Satisfies both general updates and the specific "update issue status" requirement.
    
    Args:
        issue_id: ID of the issue to update.
        update_data: Dictionary containing fields to update (e.g., {"status": "IN_PROGRESS"}).
        
    Returns:
        A dictionary confirming the update.
    """
    logger.info(f"Updating issue {issue_id} with data: {update_data}")
    
    mapped_updates = {}
    for key, value in update_data.items():
        if key == "status":
            try:
                # Handle both string and enum input
                mapped_updates["status"] = IssueStatus(value.upper()) if isinstance(value, str) else value
            except ValueError:
                logger.error(f"Invalid status: {value}")
                raise ValueError(f"Invalid status: {value}")
        elif hasattr(Issue, key):
            mapped_updates[key] = value

    if not mapped_updates:
        logger.warning(f"No valid fields to update for issue {issue_id}")
        return {"issue_id": issue_id, "status": "no_change"}

    async with AsyncSessionLocal() as db:
        try:
            stmt = (
                sa_update(Issue)
                .where(Issue.id == int(issue_id))
                .values(**mapped_updates)
            )
            await db.execute(stmt)
            await db.commit()
            
            return {
                "issue_id": issue_id,
                "status": "updated",
                "updated_fields": list(mapped_updates.keys())
            }
        except Exception as exc:
            await db.rollback()
            logger.error(f"Failed to update issue {issue_id}: {exc}")
            raise
