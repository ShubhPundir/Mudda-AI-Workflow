"""
Pydantic schemas for RAG service communication
"""
from pydantic import BaseModel, Field, UUID4
from typing import Optional


class RAGDocumentData(BaseModel):
    """Schema for document data sent to RAG service"""
    text: str = Field(..., min_length=1, description="Document text content")
    heading: str = Field(..., min_length=1, max_length=255, description="Document heading")
    author: str = Field(..., min_length=1, max_length=255, description="Document author")
    original_id: str = Field(..., description="Original document UUID from PostgreSQL")
    status: str = Field(default="active", max_length=50, description="Document status")


class RAGUpsertRequest(BaseModel):
    """Schema for RAG service upsert request"""
    document: RAGDocumentData = Field(..., description="Document data to upsert")
    namespace: str = Field(..., max_length=50, description="Document namespace")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document": {
                    "text": "Sample document content",
                    "heading": "Sample Document",
                    "author": "John Doe",
                    "original_id": "123e4567-e89b-12d3-a456-426614174000",
                    "status": "active"
                },
                "namespace": "waterworks-department"
            }
        }


class RAGDeleteRequest(BaseModel):
    """Schema for RAG service delete request (if needed)"""
    document_id: str = Field(..., description="Document UUID to delete")
    namespace: Optional[str] = Field(None, description="Optional namespace filter")
