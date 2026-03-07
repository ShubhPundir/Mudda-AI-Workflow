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


class RAGSearchRequest(BaseModel):
    """Schema for RAG service search request"""
    query: str = Field(..., min_length=1, description="Search query text")
    top_k: int = Field(default=5, ge=1, le=100, description="Number of top results to return")
    similarity_threshold: float = Field(default=0.6, ge=0.0, le=1.0, description="Minimum similarity score threshold")
    namespace: str = Field(..., min_length=1, max_length=50, description="Document namespace to search in")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "ground water withdrawal regulations",
                "top_k": 5,
                "similarity_threshold": 0.6,
                "namespace": "waterworks-department"
            }
        }


class RAGRelevantPart(BaseModel):
    """Schema for a single relevant document part in search results"""
    document_id: str = Field(..., description="Document UUID")
    text: str = Field(..., description="Relevant text content")
    heading: str = Field(..., description="Document heading")
    author: str = Field(..., description="Document author")
    chunk_index: Optional[float] = Field(None, description="Chunk index if document is chunked")
    original_id: str = Field(..., description="Original document ID")
    is_chunk: bool = Field(default=False, description="Whether this is a chunk of a larger document")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    status: str = Field(..., description="Document status")
    source: str = Field(..., description="Source of the result (e.g., 'hybrid', 'semantic', 'lexical')")
    semantic_score: float = Field(default=0.0, ge=0.0, description="Semantic similarity score")
    lexical_score: float = Field(default=0.0, ge=0.0, description="Lexical similarity score")
    combined_score: float = Field(default=0.0, ge=0.0, description="Combined similarity score")


class RAGSearchResponse(BaseModel):
    """Schema for RAG service search response"""
    relevant_parts: list[RAGRelevantPart] = Field(..., description="List of relevant document parts")
    total_results: int = Field(..., ge=0, description="Total number of results returned")
    
    class Config:
        json_schema_extra = {
            "example": {
                "relevant_parts": [
                    {
                        "document_id": "a5796ae4-3ea0-46f1-a25b-2dfe1bd25427",
                        "text": "500 m3/day in Over-exploited areas...",
                        "heading": "Haryana Water Resources Authority",
                        "author": "Shubh Pundir",
                        "chunk_index": 18.0,
                        "original_id": "a5796ae4-3ea0-46f1-a25b-2dfe1bd25427",
                        "is_chunk": True,
                        "similarity_score": 1.0,
                        "status": "active",
                        "source": "hybrid",
                        "semantic_score": 0.0,
                        "lexical_score": 0.0,
                        "combined_score": 0.0
                    }
                ],
                "total_results": 1
            }
        }
