"""
Document Router Module

This module defines the FastAPI router for document CRUD operations.
It provides HTTP REST endpoints for creating, reading, updating, and deleting documents.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sessions.database import get_db
from services.document_service import DocumentService
from infrastructure.rag import get_rag_client
from infrastructure.rag.rag_client import RAGClient
from schemas.document_schema import DocumentCreate, DocumentResponse, DocumentListResponse
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/documents", tags=["documents"])


def get_document_service(
    db: AsyncSession = Depends(get_db),
    rag_client: RAGClient = Depends(get_rag_client)
) -> DocumentService:
    """
    Dependency function to create a DocumentService instance.
    
    This function is used by FastAPI's dependency injection system to provide
    a DocumentService instance to endpoint handlers. It automatically manages
    the database session and RAG client lifecycle.
    
    Args:
        db: SQLAlchemy async database session (injected by FastAPI)
        rag_client: RAG client instance for synchronization (injected by FastAPI)
    
    Returns:
        DocumentService: Configured service instance for document operations
    
    Example:
        @router.post("/")
        async def create_document(
            document: DocumentCreate,
            service: DocumentService = Depends(get_document_service)
        ):
            return await service.upsert_document(document)
    """
    return DocumentService(db, rag_client)


@router.post("/", response_model=DocumentResponse, status_code=200)
async def upsert_document(
    document: DocumentCreate,
    service: DocumentService = Depends(get_document_service)
):
    """
    Create a new document or update an existing one (upsert operation).
    
    This endpoint accepts document data and either creates a new document or updates
    an existing one based on whether an ID is provided and whether that ID exists
    in the database.
    
    Behavior:
    - If no ID is provided: Generates a new UUID and creates a new document
    - If ID is provided and exists: Updates the existing document with new data
    - If ID is provided but doesn't exist: Creates a new document with that ID
    
    After successful database operation, the document is synchronized with the
    RAG service. RAG synchronization failures are logged but do not fail the request.
    
    Args:
        document: DocumentCreate schema with document fields (text, heading, author, optional id)
        service: DocumentService instance (injected by FastAPI)
    
    Returns:
        DocumentResponse with the created/updated document data including:
        - id: UUID of the document
        - text: Document text content
        - heading: Document heading
        - author: Document author
        - status: Document status (defaults to "active")
        - created_at: Timestamp when document was created
        - updated_at: Timestamp when document was last updated
    
    Raises:
        HTTPException 400: If required fields are missing or invalid
        HTTPException 500: If database operation fails
    
    Example:
        POST /documents
        {
            "text": "Sample document content",
            "heading": "Sample Document",
            "author": "John Doe"
        }
        
        Response (200):
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "text": "Sample document content",
            "heading": "Sample Document",
            "author": "John Doe",
            "status": "active",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
    """
    try:
        return await service.upsert_document(document)
    except Exception as e:
        logger.error(f"Error upserting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service)
):
    """
    Retrieve a document by its ID.
    
    This endpoint fetches a single document from the database using its unique
    identifier (UUID). If the document exists, it returns the complete document
    data. If the document is not found, it returns a 404 error.
    
    Args:
        document_id: UUID of the document to retrieve (path parameter)
        service: DocumentService instance (injected by FastAPI)
    
    Returns:
        DocumentResponse with the document data including:
        - id: UUID of the document
        - text: Document text content
        - heading: Document heading
        - author: Document author
        - status: Document status
        - created_at: Timestamp when document was created
        - updated_at: Timestamp when document was last updated
    
    Raises:
        HTTPException 404: If document with the specified ID does not exist
        HTTPException 422: If document_id is not a valid UUID format
    
    Example:
        GET /documents/123e4567-e89b-12d3-a456-426614174000
        
        Response (200):
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "text": "Sample document content",
            "heading": "Sample Document",
            "author": "John Doe",
            "status": "active",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
        
        Response (404):
        {
            "detail": "Document not found"
        }
    """
    logger.debug(f"GET request for document ID: {document_id}")
    document = await service.get_document(document_id)
    if not document:
        logger.warning(f"Document {document_id} not found")
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=100, description="Number of documents per page"),
    service: DocumentService = Depends(get_document_service)
):
    """
    Retrieve a paginated list of all documents.
    
    This endpoint returns a paginated list of documents ordered by creation date
    (newest first). It supports pagination through query parameters to efficiently
    handle large document collections.
    
    Pagination Parameters:
    - page: Page number starting from 1 (default: 1, minimum: 1)
    - page_size: Number of documents per page (default: 50, range: 1-100)
    
    The response includes the list of documents for the requested page, the total
    count of all documents, and the pagination parameters used.
    
    Args:
        page: Page number (1-indexed, must be >= 1)
        page_size: Number of documents per page (must be between 1 and 100)
        service: DocumentService instance (injected by FastAPI)
    
    Returns:
        DocumentListResponse containing:
        - documents: List of DocumentResponse objects for the requested page
        - total: Total count of all documents in the database
        - page: The page number that was requested
        - page_size: The page size that was used
    
    Raises:
        HTTPException 422: If page < 1 or page_size not in range 1-100
        HTTPException 500: If database operation fails
    
    Example:
        GET /documents?page=1&page_size=10
        
        Response (200):
        {
            "documents": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "text": "Sample document content",
                    "heading": "Sample Document",
                    "author": "John Doe",
                    "status": "active",
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T10:30:00Z"
                }
            ],
            "total": 42,
            "page": 1,
            "page_size": 10
        }
    """
    logger.debug(f"GET request for documents list: page={page}, page_size={page_size}")
    try:
        documents, total = await service.list_documents(page, page_size)
        return DocumentListResponse(
            documents=documents,
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{document_id}", status_code=200)
async def delete_document(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service)
):
    """
    Delete a document by its ID.
    
    This endpoint removes a document from the database using its unique identifier
    (UUID). If the document exists, it is deleted and a success message is returned.
    If the document is not found, it returns a 404 error.
    
    After successful database deletion, the document is removed from the RAG service.
    RAG synchronization failures are logged but do not fail the delete operation.
    
    Args:
        document_id: UUID of the document to delete (path parameter)
        service: DocumentService instance (injected by FastAPI)
    
    Returns:
        JSON response with success message and deleted document ID:
        {
            "message": "Document deleted successfully",
            "id": "123e4567-e89b-12d3-a456-426614174000"
        }
    
    Raises:
        HTTPException 404: If document with the specified ID does not exist
        HTTPException 422: If document_id is not a valid UUID format
    
    Example:
        DELETE /documents/123e4567-e89b-12d3-a456-426614174000
        
        Response (200):
        {
            "message": "Document deleted successfully",
            "id": "123e4567-e89b-12d3-a456-426614174000"
        }
        
        Response (404):
        {
            "detail": "Document not found"
        }
    """
    logger.debug(f"DELETE request for document ID: {document_id}")
    success = await service.delete_document(document_id)
    if not success:
        logger.warning(f"Document {document_id} not found for deletion")
        raise HTTPException(status_code=404, detail="Document not found")
    logger.info(f"Document {document_id} deleted successfully")
    return {"message": "Document deleted successfully", "id": str(document_id)}
