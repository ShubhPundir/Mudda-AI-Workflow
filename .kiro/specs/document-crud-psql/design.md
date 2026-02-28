# Design Document: Document CRUD Service with RAG Synchronization

## Overview

The Document CRUD Service is a Python FastAPI application that provides HTTP REST endpoints for managing text documents in PostgreSQL. The service implements create, read, update, and delete operations with automatic synchronization to an external RAG (Retrieval-Augmented Generation) service. The design follows the existing codebase patterns using SQLAlchemy async ORM, FastAPI routers, and environment-based configuration.

The service runs on port 8081 and integrates with:
- PostgreSQL database for persistent document storage
- RAG service on port 8082 for document indexing and retrieval
- Support for both HTTP REST and gRPC communication protocols

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│  Client Apps    │
└────────┬────────┘
         │ HTTP REST
         ▼
┌─────────────────────────────────────┐
│   Document Service (Port 8081)      │
│  ┌──────────────────────────────┐   │
│  │  FastAPI Router Layer        │   │
│  │  - POST /documents           │   │
│  │  - GET /documents/{id}       │   │
│  │  - GET /documents            │   │
│  │  - DELETE /documents/{id}    │   │
│  └──────────┬───────────────────┘   │
│             ▼                        │
│  ┌──────────────────────────────┐   │
│  │  Service Layer               │   │
│  │  - Validation                │   │
│  │  - Business Logic            │   │
│  └──────────┬───────────────────┘   │
│             ▼                        │
│  ┌──────────────────────────────┐   │
│  │  Data Access Layer           │   │
│  │  - SQLAlchemy ORM            │   │
│  │  - Async Sessions            │   │
│  └──────────┬───────────────────┘   │
└─────────────┼───────────────────────┘
              │
    ┌─────────┴─────────┐
    ▼                   ▼
┌─────────┐      ┌──────────────┐
│PostgreSQL│      │ RAG Service  │
│Database  │      │ (Port 8082)  │
└──────────┘      └──────────────┘
```

### Component Layers

1. **Router Layer**: FastAPI endpoints handling HTTP requests and responses
2. **Service Layer**: Business logic, validation, and orchestration
3. **Data Access Layer**: SQLAlchemy models and database operations
4. **Infrastructure Layer**: RAG service client (HTTP/gRPC)
5. **Configuration Layer**: Environment-based settings management

## Components and Interfaces

### 1. Document Model (backend/models/document.py)

SQLAlchemy ORM model representing the documents table.

```python
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from .base import Base

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text = Column(Text, nullable=False)
    heading = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
```

### 2. Document Schemas (backend/schemas/document_schema.py)

Pydantic models for request/response validation.

```python
from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from typing import Optional

class DocumentBase(BaseModel):
    text: str = Field(..., min_length=1, description="Document text content")
    heading: str = Field(..., min_length=1, max_length=255, description="Document heading")
    author: str = Field(..., min_length=1, max_length=255, description="Document author")
    status: str = Field(default="active", max_length=50, description="Document status")

class DocumentCreate(DocumentBase):
    id: Optional[UUID4] = Field(None, description="Optional document ID for upsert")

class DocumentResponse(DocumentBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int
    page: int
    page_size: int
```

### 3. Document Service (backend/services/document_service.py)

Business logic layer handling document operations and RAG synchronization.

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from models.document import Document
from schemas.document_schema import DocumentCreate, DocumentResponse
from infrastructure.rag.rag_client import RAGClient
import uuid
import logging

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self, db: AsyncSession, rag_client: RAGClient):
        self.db = db
        self.rag_client = rag_client
    
    async def upsert_document(self, document_data: DocumentCreate) -> DocumentResponse:
        # Generate ID if not provided
        doc_id = document_data.id or uuid.uuid4()
        
        # Check if document exists
        result = await self.db.execute(select(Document).where(Document.id == doc_id))
        existing_doc = result.scalar_one_or_none()
        
        if existing_doc:
            # Update existing document
            for key, value in document_data.dict(exclude_unset=True, exclude={'id'}).items():
                setattr(existing_doc, key, value)
            document = existing_doc
        else:
            # Create new document
            document = Document(id=doc_id, **document_data.dict(exclude={'id'}))
            self.db.add(document)
        
        await self.db.commit()
        await self.db.refresh(document)
        
        # Sync to RAG service (non-blocking)
        await self._sync_to_rag_upsert(document)
        
        return DocumentResponse.from_orm(document)
    
    async def get_document(self, document_id: uuid.UUID) -> Optional[DocumentResponse]:
        result = await self.db.execute(select(Document).where(Document.id == document_id))
        document = result.scalar_one_or_none()
        return DocumentResponse.from_orm(document) if document else None
    
    async def list_documents(self, page: int = 1, page_size: int = 50) -> tuple[list[DocumentResponse], int]:
        # Get total count
        count_result = await self.db.execute(select(func.count(Document.id)))
        total = count_result.scalar()
        
        # Get paginated results
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(Document).offset(offset).limit(page_size).order_by(Document.created_at.desc())
        )
        documents = result.scalars().all()
        
        return [DocumentResponse.from_orm(doc) for doc in documents], total
    
    async def delete_document(self, document_id: uuid.UUID) -> bool:
        result = await self.db.execute(select(Document).where(Document.id == document_id))
        document = result.scalar_one_or_none()
        
        if not document:
            return False
        
        await self.db.delete(document)
        await self.db.commit()
        
        # Sync to RAG service (non-blocking)
        await self._sync_to_rag_delete(document_id)
        
        return True
    
    async def _sync_to_rag_upsert(self, document: Document):
        try:
            await self.rag_client.upsert_document({
                "id": str(document.id),
                "text": document.text,
                "heading": document.heading,
                "author": document.author,
                "status": document.status
            })
        except Exception as e:
            logger.error(f"Failed to sync document {document.id} to RAG service: {e}")
    
    async def _sync_to_rag_delete(self, document_id: uuid.UUID):
        try:
            await self.rag_client.delete_document(str(document_id))
        except Exception as e:
            logger.error(f"Failed to delete document {document_id} from RAG service: {e}")
```

### 4. RAG Client (backend/infrastructure/rag/rag_client.py)

Abstract interface and implementations for RAG service communication.

```python
from abc import ABC, abstractmethod
from typing import Dict
import httpx
import logging

logger = logging.getLogger(__name__)

class RAGClient(ABC):
    @abstractmethod
    async def upsert_document(self, document_data: Dict) -> None:
        pass
    
    @abstractmethod
    async def delete_document(self, document_id: str) -> None:
        pass

class HTTPRAGClient(RAGClient):
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def upsert_document(self, document_data: Dict) -> None:
        url = f"{self.base_url}/documents/upsert"
        response = await self.client.post(url, json=document_data)
        response.raise_for_status()
    
    async def delete_document(self, document_id: str) -> None:
        url = f"{self.base_url}/documents/{document_id}"
        response = await self.client.delete(url)
        response.raise_for_status()
    
    async def close(self):
        await self.client.aclose()

class GRPCRAGClient(RAGClient):
    def __init__(self, grpc_address: str):
        self.grpc_address = grpc_address
        # gRPC channel and stub initialization would go here
        # This is a placeholder for gRPC implementation
    
    async def upsert_document(self, document_data: Dict) -> None:
        # gRPC call implementation
        pass
    
    async def delete_document(self, document_id: str) -> None:
        # gRPC call implementation
        pass
```

### 5. Document Router (backend/routers/document_router.py)

FastAPI router defining HTTP endpoints.

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sessions.database import get_db
from services.document_service import DocumentService
from schemas.document_schema import DocumentCreate, DocumentResponse, DocumentListResponse
from infrastructure.rag.rag_client import get_rag_client
from uuid import UUID

router = APIRouter(prefix="/documents", tags=["documents"])

def get_document_service(
    db: AsyncSession = Depends(get_db),
    rag_client = Depends(get_rag_client)
) -> DocumentService:
    return DocumentService(db, rag_client)

@router.post("/", response_model=DocumentResponse, status_code=200)
async def upsert_document(
    document: DocumentCreate,
    service: DocumentService = Depends(get_document_service)
):
    try:
        return await service.upsert_document(document)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service)
):
    document = await service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: DocumentService = Depends(get_document_service)
):
    documents, total = await service.list_documents(page, page_size)
    return DocumentListResponse(
        documents=documents,
        total=total,
        page=page,
        page_size=page_size
    )

@router.delete("/{document_id}", status_code=200)
async def delete_document(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service)
):
    success = await service.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted successfully", "id": str(document_id)}
```

### 6. Configuration Updates (backend/config.py)

Add RAG service configuration to existing Settings class.

```python
# Add to Settings class:
RAG_SERVICE_URL: str = os.getenv("RAG_SERVICE_URL", "http://localhost:8082")
RAG_PROTOCOL: str = os.getenv("RAG_PROTOCOL", "http")  # "http" or "grpc"
RAG_GRPC_ADDRESS: str = os.getenv("RAG_GRPC_ADDRESS", "localhost:8082")
```

### 7. RAG Client Factory (backend/infrastructure/rag/__init__.py)

Factory function for dependency injection.

```python
from config import settings
from .rag_client import RAGClient, HTTPRAGClient, GRPCRAGClient

_rag_client_instance = None

def get_rag_client() -> RAGClient:
    global _rag_client_instance
    if _rag_client_instance is None:
        if settings.RAG_PROTOCOL == "grpc":
            _rag_client_instance = GRPCRAGClient(settings.RAG_GRPC_ADDRESS)
        else:
            _rag_client_instance = HTTPRAGClient(settings.RAG_SERVICE_URL)
    return _rag_client_instance
```

## Data Models

### Database Schema

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    text TEXT NOT NULL,
    heading VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);
```

### Document Entity

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique document identifier |
| text | TEXT | NOT NULL | Document text content |
| heading | VARCHAR(255) | NOT NULL | Document heading/title |
| author | VARCHAR(255) | NOT NULL | Document author name |
| status | VARCHAR(50) | NOT NULL, DEFAULT 'active' | Document status |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Document Creation Round-Trip

*For any* valid document data (text, heading, author), creating a document and then retrieving it by ID should return equivalent document data with all fields populated (id as UUID, text, heading, author, status, created_at, updated_at).

**Validates: Requirements 1.2, 2.2, 2.4, 3.1, 3.5**

### Property 2: Default Status Assignment

*For any* document created without an explicit status field, the returned document should have status set to "active".

**Validates: Requirements 1.3**

### Property 3: Timestamp Management on Creation

*For any* newly created document, the created_at timestamp should be set and should be within a reasonable time window (e.g., 5 seconds) of the current time.

**Validates: Requirements 1.4**

### Property 4: Timestamp Update on Modification

*For any* existing document that is updated via upsert, the updated_at timestamp should be later than the original updated_at timestamp and should be within a reasonable time window of the current time.

**Validates: Requirements 1.5**

### Property 5: Required Field Validation

*For any* document creation request missing one or more required fields (text, heading, or author), the service should return HTTP status 400 with a descriptive error message.

**Validates: Requirements 2.1, 2.5, 6.1**

### Property 6: Upsert Update Behavior

*For any* existing document, upserting with the same ID but different field values should result in the document being updated with the new values while preserving the same ID and created_at timestamp.

**Validates: Requirements 2.3**

### Property 7: Non-Existent Document Returns 404

*For any* UUID that does not correspond to an existing document, GET and DELETE requests should return HTTP status 404.

**Validates: Requirements 3.2, 4.3**

### Property 8: Pagination Correctness

*For any* set of documents in the database, requesting different pages with a given page_size should return non-overlapping subsets of documents, and the sum of all pages should equal the total document count.

**Validates: Requirements 3.3, 3.4**

### Property 9: Delete Removes Document

*For any* existing document, after a successful DELETE operation, subsequent GET requests for that document ID should return HTTP status 404.

**Validates: Requirements 4.1, 4.2**

### Property 10: RAG Service Synchronization

*For any* successful document upsert or delete operation, the corresponding RAG service endpoint (upsert or delete) should be called with the correct document data or ID, regardless of whether the RAG call succeeds or fails.

**Validates: Requirements 2.6, 4.4, 5.1, 5.2**

### Property 11: RAG Service Failure Resilience

*For any* document operation where the RAG service is unavailable or returns an error, the primary CRUD operation should still succeed and return the appropriate success status, and the error should be logged.

**Validates: Requirements 5.5, 6.3**

### Property 12: UUID Validation

*For any* request with a document_id parameter that is not a valid UUID format, the service should return an appropriate error response (HTTP status 400 or 422).

**Validates: Requirements 6.5**

### Property 13: Database Session Lifecycle

*For any* database operation (successful or failed), the database session should be properly closed and resources released, preventing connection leaks.

**Validates: Requirements 8.5**

## Error Handling

### Error Categories

1. **Validation Errors (HTTP 400)**
   - Missing required fields (text, heading, author)
   - Invalid UUID format for document_id
   - Invalid pagination parameters (negative page numbers, page_size > 100)

2. **Not Found Errors (HTTP 404)**
   - Document ID does not exist for GET or DELETE operations

3. **Server Errors (HTTP 500)**
   - Database connection failures
   - Database query execution failures
   - Unexpected exceptions during request processing

4. **External Service Errors (Logged, Non-Blocking)**
   - RAG service unavailable
   - RAG service returns error response
   - Network timeout communicating with RAG service

### Error Response Format

All error responses follow a consistent JSON structure:

```json
{
  "detail": "Human-readable error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Handling Strategy

1. **Input Validation**: Validate all inputs at the router layer using Pydantic schemas
2. **Database Errors**: Catch SQLAlchemy exceptions and return 500 with generic error message (avoid exposing internal details)
3. **RAG Service Errors**: Catch all exceptions from RAG client, log with full details, continue with CRUD operation
4. **Resource Cleanup**: Use try-finally blocks to ensure database sessions are closed
5. **Logging**: Log all errors with appropriate severity levels (ERROR for failures, WARNING for RAG sync issues)

### Graceful Degradation

The service prioritizes the primary CRUD operations over RAG synchronization:
- If RAG service is down, documents can still be created, read, updated, and deleted
- RAG synchronization failures are logged but do not fail the request
- This ensures the document service remains available even when dependencies are unavailable

## Testing Strategy

### Dual Testing Approach

The testing strategy employs both unit tests and property-based tests to ensure comprehensive coverage:

- **Unit tests**: Verify specific examples, edge cases, and error conditions
- **Property tests**: Verify universal properties across all inputs using randomized test data
- Both approaches are complementary and necessary for thorough validation

### Property-Based Testing

**Framework**: Use `hypothesis` library for Python property-based testing

**Configuration**:
- Minimum 100 iterations per property test
- Each test tagged with format: `# Feature: document-crud-psql, Property {N}: {property_text}`
- Each correctness property implemented as a single property-based test

**Test Data Generation**:
- Random UUIDs for document IDs
- Random strings (1-1000 chars) for text content
- Random strings (1-255 chars) for heading and author
- Random valid/invalid field combinations for validation testing
- Random pagination parameters

**Property Test Examples**:

```python
from hypothesis import given, strategies as st
import pytest

# Feature: document-crud-psql, Property 1: Document Creation Round-Trip
@given(
    text=st.text(min_size=1, max_size=1000),
    heading=st.text(min_size=1, max_size=255),
    author=st.text(min_size=1, max_size=255)
)
async def test_document_creation_round_trip(text, heading, author):
    # Create document
    response = await client.post("/documents", json={
        "text": text,
        "heading": heading,
        "author": author
    })
    assert response.status_code == 200
    created_doc = response.json()
    doc_id = created_doc["id"]
    
    # Retrieve document
    response = await client.get(f"/documents/{doc_id}")
    assert response.status_code == 200
    retrieved_doc = response.json()
    
    # Verify equivalence
    assert retrieved_doc["text"] == text
    assert retrieved_doc["heading"] == heading
    assert retrieved_doc["author"] == author
    assert retrieved_doc["id"] == doc_id
    assert "created_at" in retrieved_doc
    assert "updated_at" in retrieved_doc
```

### Unit Testing

**Framework**: Use `pytest` with `pytest-asyncio` for async test support

**Test Categories**:

1. **Happy Path Tests**
   - Create document with all fields
   - Retrieve existing document
   - Update document via upsert
   - Delete existing document
   - List documents with pagination

2. **Edge Cases**
   - Empty database list
   - Single document in database
   - Maximum length strings for heading/author
   - Very large text content
   - Page beyond available results

3. **Error Conditions**
   - Missing required fields
   - Invalid UUID format
   - Non-existent document ID
   - Database connection failure (mocked)
   - RAG service failure (mocked)

4. **Integration Tests**
   - RAG service receives correct data on upsert
   - RAG service receives correct ID on delete
   - HTTP vs gRPC protocol selection
   - Configuration loading from environment

**Mocking Strategy**:
- Mock RAG client for testing synchronization behavior
- Mock database for testing error handling
- Use test database for integration tests
- Mock external HTTP/gRPC calls

### Test Organization

```
backend/test/
├── test_document_model.py          # Model unit tests
├── test_document_service.py        # Service layer unit tests
├── test_document_router.py         # Router/endpoint unit tests
├── test_document_properties.py     # Property-based tests
├── test_rag_client.py              # RAG client unit tests
└── conftest.py                     # Shared fixtures and configuration
```

### Test Coverage Goals

- Minimum 90% code coverage for service and router layers
- 100% coverage of error handling paths
- All 13 correctness properties implemented as property tests
- All edge cases covered by unit tests

### Continuous Integration

- Run all tests on every commit
- Property tests run with 100 iterations in CI
- Integration tests run against test database
- Coverage reports generated and tracked over time
