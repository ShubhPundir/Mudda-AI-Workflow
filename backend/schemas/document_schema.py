"""
Pydantic schemas for document CRUD operations
"""
from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from typing import Optional


class DocumentBase(BaseModel):
    """Base schema with common document fields"""
    text: str = Field(..., min_length=1, description="Document text content")
    heading: str = Field(..., min_length=1, max_length=255, description="Document heading")
    author: str = Field(..., min_length=1, max_length=255, description="Document author")
    status: str = Field(default="active", max_length=50, description="Document status")
    namespace: str = Field(default="waterworks-department", max_length=50, description="Document namespace")


class DocumentCreate(DocumentBase):
    """Schema for creating or upserting a document"""
    id: Optional[UUID4] = Field(None, description="Optional document ID for upsert")


class DocumentResponse(DocumentBase):
    """Schema for document response with all fields"""
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Schema for paginated list of documents"""
    documents: list[DocumentResponse]
    total: int
    page: int
    page_size: int
