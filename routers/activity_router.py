from fastapi import APIRouter
from typing import List, Dict, Any
from activities.registry import ACTIVITY_METADATA

router = APIRouter(prefix="/activities", tags=["activities"])

@router.get("/", response_model=List[Dict[str, Any]])
async def get_activities():
    """
    Get all available activities from the registry.
    """
    # Convert dict to list of dicts and inject the key as 'id' to match frontend expectations
    activities = [{"id": k, **v} for k, v in ACTIVITY_METADATA.items()]
    return activities
