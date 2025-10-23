"""
Component management router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sessions.database import get_db
from services import ComponentService
from schemas import ComponentCreateRequest, ComponentResponse

router = APIRouter(prefix="/components", tags=["components"])


@router.post("", response_model=ComponentResponse)
async def create_component(
    request: ComponentCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new API component
    
    Args:
        request: Component creation data
        db: Database session
        
    Returns:
        Created component details
    """
    try:
        component_service = ComponentService(db)
        return component_service.create_component(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create component: {str(e)}"
        )


@router.get("", response_model=List[ComponentResponse])
async def list_components(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    List all available components
    
    Args:
        active_only: Whether to return only active components
        db: Database session
        
    Returns:
        List of components
    """
    try:
        print("list_components", active_only)
        component_service = ComponentService(db)
        return component_service.list_components(active_only)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list components: {str(e)}"
        )


@router.get("/{component_id}", response_model=ComponentResponse)
async def get_component(
    component_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific component by ID
    
    Args:
        component_id: UUID of the component
        db: Database session
        
    Returns:
        Component details
    """
    try:
        component_service = ComponentService(db)
        component = component_service.get_component(component_id)
        
        if not component:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Component not found"
            )
        
        return component
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get component: {str(e)}"
        )
