"""
Unit tests for Document Router endpoints.

Tests the FastAPI router endpoints for document CRUD operations.
"""
import pytest
import uuid
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from httpx import AsyncClient
from datetime import datetime

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from main import app
from services.document_service import DocumentService
from schemas.document_schema import DocumentCreate, DocumentResponse


# --------------------------------------------------------------------------
# Test POST /documents endpoint
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_post_documents_creates_new_document():
    """Verify POST /documents creates a new document successfully."""
    # Arrange
    document_data = {
        "text": "Test document content",
        "heading": "Test Heading",
        "author": "Test Author"
    }
    
    # Mock the service response
    mock_response = DocumentResponse(
        id=uuid.uuid4(),
        text=document_data["text"],
        heading=document_data["heading"],
        author=document_data["author"],
        status="active",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Create mock service
    mock_service = AsyncMock()
    mock_service.upsert_document = AsyncMock(return_value=mock_response)
    
    # Override the dependency
    from routers.document_router import get_document_service
    app.dependency_overrides[get_document_service] = lambda: mock_service
    
    try:
        # Act
        from httpx import ASGITransport
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/documents/", json=document_data)
        
        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["text"] == document_data["text"]
        assert response_data["heading"] == document_data["heading"]
        assert response_data["author"] == document_data["author"]
        assert response_data["status"] == "active"
        assert "id" in response_data
        assert "created_at" in response_data
        assert "updated_at" in response_data
    finally:
        # Clean up override
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_post_documents_with_id_updates_existing():
    """Verify POST /documents with ID updates existing document."""
    # Arrange
    doc_id = uuid.uuid4()
    document_data = {
        "id": str(doc_id),
        "text": "Updated content",
        "heading": "Updated Heading",
        "author": "Updated Author"
    }
    
    # Mock the service response
    mock_response = DocumentResponse(
        id=doc_id,
        text=document_data["text"],
        heading=document_data["heading"],
        author=document_data["author"],
        status="active",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Create mock service
    mock_service = AsyncMock()
    mock_service.upsert_document = AsyncMock(return_value=mock_response)
    
    # Override the dependency
    from routers.document_router import get_document_service
    app.dependency_overrides[get_document_service] = lambda: mock_service
    
    try:
        # Act
        from httpx import ASGITransport
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/documents/", json=document_data)
        
        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == str(doc_id)
        assert response_data["text"] == document_data["text"]
    finally:
        # Clean up override
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_post_documents_returns_400_for_missing_required_fields():
    """Verify POST /documents returns 400 when required fields are missing."""
    # Arrange - missing 'text' field
    document_data = {
        "heading": "Test Heading",
        "author": "Test Author"
    }
    
    # Act
    from httpx import ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/documents/", json=document_data)
    
    # Assert
    assert response.status_code == 422  # FastAPI validation error


@pytest.mark.asyncio
async def test_post_documents_returns_500_on_service_error():
    """Verify POST /documents returns 500 when service raises exception."""
    # Arrange
    document_data = {
        "text": "Test content",
        "heading": "Test Heading",
        "author": "Test Author"
    }
    
    # Create mock service that raises exception
    mock_service = AsyncMock()
    mock_service.upsert_document = AsyncMock(side_effect=Exception("Database connection failed"))
    
    # Override the dependency
    from routers.document_router import get_document_service
    app.dependency_overrides[get_document_service] = lambda: mock_service
    
    try:
        # Act
        from httpx import ASGITransport
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/documents/", json=document_data)
        
        # Assert
        assert response.status_code == 500
        assert "Database connection failed" in response.json()["detail"]
    finally:
        # Clean up override
        app.dependency_overrides.clear()



# --------------------------------------------------------------------------
# Test GET /documents/{document_id} endpoint
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_document_returns_document_when_found():
    """Verify GET /documents/{document_id} returns document when it exists."""
    # Arrange
    doc_id = uuid.uuid4()
    mock_response = DocumentResponse(
        id=doc_id,
        text="Test document content",
        heading="Test Heading",
        author="Test Author",
        status="active",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Mock the service method
    with patch('routers.document_router.DocumentService') as mock_service_class:
        mock_service = AsyncMock()
        mock_service.get_document = AsyncMock(return_value=mock_response)
        mock_service_class.return_value = mock_service
        
        # Act
        from httpx import ASGITransport
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/documents/{doc_id}")
        
        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == str(doc_id)
        assert response_data["text"] == "Test document content"
        assert response_data["heading"] == "Test Heading"
        assert response_data["author"] == "Test Author"
        assert response_data["status"] == "active"
        assert "created_at" in response_data
        assert "updated_at" in response_data


@pytest.mark.asyncio
async def test_get_document_returns_404_when_not_found():
    """Verify GET /documents/{document_id} returns 404 when document doesn't exist."""
    # Arrange
    doc_id = uuid.uuid4()
    
    # Mock the service method to return None
    with patch('routers.document_router.DocumentService') as mock_service_class:
        mock_service = AsyncMock()
        mock_service.get_document = AsyncMock(return_value=None)
        mock_service_class.return_value = mock_service
        
        # Act
        from httpx import ASGITransport
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/documents/{doc_id}")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Document not found"


@pytest.mark.asyncio
async def test_get_document_returns_422_for_invalid_uuid():
    """Verify GET /documents/{document_id} returns 422 for invalid UUID format."""
    # Arrange
    invalid_id = "not-a-valid-uuid"
    
    # Act
    from httpx import ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/documents/{invalid_id}")
    
    # Assert
    assert response.status_code == 422  # FastAPI validation error



# --------------------------------------------------------------------------
# Test GET /documents endpoint (list with pagination)
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_documents_returns_paginated_list():
    """Verify GET /documents returns paginated list of documents."""
    # Arrange
    mock_documents = [
        DocumentResponse(
            id=uuid.uuid4(),
            text=f"Document {i}",
            heading=f"Heading {i}",
            author=f"Author {i}",
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        for i in range(3)
    ]
    
    # Mock the service method
    with patch('routers.document_router.DocumentService') as mock_service_class:
        mock_service = AsyncMock()
        mock_service.list_documents = AsyncMock(return_value=(mock_documents, 10))
        mock_service_class.return_value = mock_service
        
        # Act
        from httpx import ASGITransport
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/documents/?page=1&page_size=3")
        
        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["documents"]) == 3
        assert response_data["total"] == 10
        assert response_data["page"] == 1
        assert response_data["page_size"] == 3


@pytest.mark.asyncio
async def test_get_documents_uses_default_pagination():
    """Verify GET /documents uses default pagination values when not specified."""
    # Arrange
    mock_documents = []
    
    # Mock the service method
    with patch('routers.document_router.DocumentService') as mock_service_class:
        mock_service = AsyncMock()
        mock_service.list_documents = AsyncMock(return_value=(mock_documents, 0))
        mock_service_class.return_value = mock_service
        
        # Act
        from httpx import ASGITransport
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/documents/")
        
        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["page"] == 1
        assert response_data["page_size"] == 50
        assert response_data["total"] == 0
        assert response_data["documents"] == []


@pytest.mark.asyncio
async def test_get_documents_validates_page_minimum():
    """Verify GET /documents returns 422 when page < 1."""
    # Act
    from httpx import ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/documents/?page=0&page_size=10")
    
    # Assert
    assert response.status_code == 422  # FastAPI validation error


@pytest.mark.asyncio
async def test_get_documents_validates_page_size_minimum():
    """Verify GET /documents returns 422 when page_size < 1."""
    # Act
    from httpx import ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/documents/?page=1&page_size=0")
    
    # Assert
    assert response.status_code == 422  # FastAPI validation error


@pytest.mark.asyncio
async def test_get_documents_validates_page_size_maximum():
    """Verify GET /documents returns 422 when page_size > 100."""
    # Act
    from httpx import ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/documents/?page=1&page_size=101")
    
    # Assert
    assert response.status_code == 422  # FastAPI validation error


@pytest.mark.asyncio
async def test_get_documents_returns_500_on_service_error():
    """Verify GET /documents returns 500 when service raises exception."""
    # Mock the service method to raise exception
    with patch('routers.document_router.DocumentService') as mock_service_class:
        mock_service = AsyncMock()
        mock_service.list_documents = AsyncMock(side_effect=Exception("Database connection failed"))
        mock_service_class.return_value = mock_service
        
        # Act
        from httpx import ASGITransport
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/documents/?page=1&page_size=10")
        
        # Assert
        assert response.status_code == 500
        assert "Database connection failed" in response.json()["detail"]



# --------------------------------------------------------------------------
# Test DELETE /documents/{document_id} endpoint
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_document_returns_success_when_found():
    """Verify DELETE /documents/{document_id} returns success when document exists."""
    # Arrange
    doc_id = uuid.uuid4()
    
    # Mock the service method
    with patch('routers.document_router.DocumentService') as mock_service_class:
        mock_service = AsyncMock()
        mock_service.delete_document = AsyncMock(return_value=True)
        mock_service_class.return_value = mock_service
        
        # Act
        from httpx import ASGITransport
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/documents/{doc_id}")
        
        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["message"] == "Document deleted successfully"
        assert response_data["id"] == str(doc_id)


@pytest.mark.asyncio
async def test_delete_document_returns_404_when_not_found():
    """Verify DELETE /documents/{document_id} returns 404 when document doesn't exist."""
    # Arrange
    doc_id = uuid.uuid4()
    
    # Mock the service method to return False
    with patch('routers.document_router.DocumentService') as mock_service_class:
        mock_service = AsyncMock()
        mock_service.delete_document = AsyncMock(return_value=False)
        mock_service_class.return_value = mock_service
        
        # Act
        from httpx import ASGITransport
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/documents/{doc_id}")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Document not found"


@pytest.mark.asyncio
async def test_delete_document_returns_422_for_invalid_uuid():
    """Verify DELETE /documents/{document_id} returns 422 for invalid UUID format."""
    # Arrange
    invalid_id = "not-a-valid-uuid"
    
    # Act
    from httpx import ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.delete(f"/documents/{invalid_id}")
    
    # Assert
    assert response.status_code == 422  # FastAPI validation error
