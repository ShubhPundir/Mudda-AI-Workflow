"""
Pydantic schemas for Component model
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Union
from datetime import datetime


class ComponentSchema(BaseModel):
    """Schema for component data"""
    id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    version: Optional[str] = "1.0"
    is_active: Optional[bool] = True
    activities: List[Dict[str, Any]] = []
    config: Optional[Dict[str, Any]] = {}
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ComponentCreateRequest(BaseModel):
    """Request schema for creating a new component"""
    name: str = Field(..., description="Friendly name of the component")
    description: Optional[str] = Field(None, description="What the component does")
    category: Optional[str] = Field(None, description="Optional category like 'Home Services'")
    version: Optional[str] = Field("1.0", description="Component version")
    activities: List[Dict[str, Any]] = Field(..., description="List of activities this component orchestrates")
    config: Optional[Dict[str, Any]] = Field({}, description="Component-wide configuration")


class ComponentResponse(BaseModel):
    """Response schema for component operations"""
    id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    version: Optional[str] = "1.0"
    is_active: bool
    activities: List[Dict[str, Any]]
    config: Optional[Dict[str, Any]] = {}
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ComponentForSelection(BaseModel):
    """Minimal schema for component selection (only id, name, description)"""
    id: str
    name: str
    description: Optional[str] = None


class ComponentForAI(BaseModel):
    """Schema for components formatted for AI processing (excludes audit fields)"""
    id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    version: Optional[str] = "1.0"
    activities: List[Dict[str, Any]]
    config: Optional[Dict[str, Any]] = {}