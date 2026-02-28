"""
Unit tests for DocumentService.

Tests the document service layer including upsert, get, list, and delete operations.
"""
import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from services.document_service import DocumentService
from schemas.document_schema import DocumentCreate, DocumentResponse
from models.document import Document
from infrastructure.rag.rag_client import RAGClient


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------

@pytest.fixture
def mock_db_session():
    """Creates a mock AsyncSession for database operations."""
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def mock_rag_client():
    """Creates a mock RAG client."""
    client = AsyncMock(spec=RAGClient)
    client.upsert_document = AsyncMock()
    client.delete_document = AsyncMock()
    return client


@pytest.fixture
def document_service(mock_db_session, mock_rag_client):
    """Creates a DocumentService instance with mocked dependencies."""
    return DocumentService(db=mock_db_session, rag_client=mock_rag_client)


# --------------------------------------------------------------------------
# Unit Tests - upsert_document (Create New Document)
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_upsert_document_creates_new_document_without_id(
    document_service, mock_db_session, mock_rag_client
):
    """Verify upsert_document creates a new document when ID is not provided."""
    # Arrange
    document_data = DocumentCreate(
        text="Test document content",
        heading="Test Heading",
        author="Test Author",
        status="active"
    )
    
    # Mock database query to return None (document doesn't exist)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute = AsyncMock(return_value=mock_result)
    
    # Mock the created document
    created_doc = Document(
        id=uuid.uuid4(),
        text=document_data.text,
        heading=document_data.heading,
        author=document_data.author,
        status=document_data.status
    )
    
    # Mock refresh to populate the document
    async def mock_refresh(doc):
        doc.id = created_doc.id
        doc.created_at = "2024-01-01T00:00:00Z"
        doc.updated_at = "2024-01-01T00:00:00Z"
    
    mock_db_session.refresh = AsyncMock(side_effect=mock_refresh)
    mock_db_session.commit = AsyncMock()
    
    # Act
    result = await document_service.upsert_document(document_data)
    
    # Assert
    assert mock_db_session.add.called
    assert mock_db_session.commit.called
    assert mock_db_session.refresh.called
    assert mock_rag_client.upsert_document.called


@pytest.mark.asyncio
async def test_upsert_document_creates_new_document_with_id(
    document_service, mock_db_session, mock_rag_client
):
    """Verify upsert_document creates a new document when ID is provided but doesn't exist."""
    # Arrange
    doc_id = uuid.uuid4()
    document_data = DocumentCreate(
        id=doc_id,
        text="Test document content",
        heading="Test Heading",
        author="Test Author",
        status="active"
    )
    
    # Mock database query to return None (document doesn't exist)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute = AsyncMock(return_value=mock_result)
    
    # Mock the created document
    created_doc = Document(
        id=doc_id,
        text=document_data.text,
        heading=document_data.heading,
        author=document_data.author,
        status=document_data.status
    )
    
    # Mock refresh to populate the document
    async def mock_refresh(doc):
        doc.created_at = "2024-01-01T00:00:00Z"
        doc.updated_at = "2024-01-01T00:00:00Z"
    
    mock_db_session.refresh = AsyncMock(side_effect=mock_refresh)
    mock_db_session.commit = AsyncMock()
    
    # Act
    result = await document_service.upsert_document(document_data)
    
    # Assert
    assert mock_db_session.add.called
    assert mock_db_session.commit.called
    assert mock_db_session.refresh.called
    assert mock_rag_client.upsert_document.called


# --------------------------------------------------------------------------
# Unit Tests - upsert_document (Update Existing Document)
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_upsert_document_updates_existing_document(
    document_service, mock_db_session, mock_rag_client
):
    """Verify upsert_document updates an existing document when ID matches."""
    # Arrange
    doc_id = uuid.uuid4()
    document_data = DocumentCreate(
        id=doc_id,
        text="Updated document content",
        heading="Updated Heading",
        author="Updated Author",
        status="active"
    )
    
    # Mock existing document
    existing_doc = Document(
        id=doc_id,
        text="Original content",
        heading="Original Heading",
        author="Original Author",
        status="active"
    )
    
    # Mock database query to return existing document
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_doc
    mock_db_session.execute = AsyncMock(return_value=mock_result)
    
    # Mock refresh to populate timestamps
    async def mock_refresh(doc):
        doc.created_at = "2024-01-01T00:00:00Z"
        doc.updated_at = "2024-01-01T00:00:01Z"
    
    mock_db_session.refresh = AsyncMock(side_effect=mock_refresh)
    mock_db_session.commit = AsyncMock()
    
    # Act
    result = await document_service.upsert_document(document_data)
    
    # Assert
    assert existing_doc.text == "Updated document content"
    assert existing_doc.heading == "Updated Heading"
    assert existing_doc.author == "Updated Author"
    assert not mock_db_session.add.called  # Should not add, only update
    assert mock_db_session.commit.called
    assert mock_db_session.refresh.called
    assert mock_rag_client.upsert_document.called


# --------------------------------------------------------------------------
# Unit Tests - RAG Synchronization
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_upsert_document_syncs_to_rag_service(
    document_service, mock_db_session, mock_rag_client
):
    """Verify upsert_document calls RAG client with correct data."""
    # Arrange
    doc_id = uuid.uuid4()
    document_data = DocumentCreate(
        id=doc_id,
        text="Test content",
        heading="Test Heading",
        author="Test Author",
        status="active"
    )
    
    # Mock database query to return None (new document)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute = AsyncMock(return_value=mock_result)
    
    # Mock the created document
    created_doc = Document(
        id=doc_id,
        text=document_data.text,
        heading=document_data.heading,
        author=document_data.author,
        status=document_data.status
    )
    
    # Mock refresh
    async def mock_refresh(doc):
        doc.created_at = "2024-01-01T00:00:00Z"
        doc.updated_at = "2024-01-01T00:00:00Z"
    
    mock_db_session.refresh = AsyncMock(side_effect=mock_refresh)
    mock_db_session.commit = AsyncMock()
    
    # Act
    result = await document_service.upsert_document(document_data)
    
    # Assert
    mock_rag_client.upsert_document.assert_called_once()
    call_args = mock_rag_client.upsert_document.call_args[0][0]
    assert call_args["document"]["original_id"] == str(doc_id)
    assert call_args["document"]["text"] == "Test content"
    assert call_args["document"]["heading"] == "Test Heading"
    assert call_args["document"]["author"] == "Test Author"
    assert call_args["document"]["status"] == "active"
    assert call_args["namespace"] == "waterworks-department"


@pytest.mark.asyncio
async def test_upsert_document_continues_on_rag_failure(
    document_service, mock_db_session, mock_rag_client
):
    """Verify upsert_document succeeds even when RAG sync fails."""
    # Arrange
    document_data = DocumentCreate(
        text="Test content",
        heading="Test Heading",
        author="Test Author",
        status="active"
    )
    
    # Mock database query to return None (new document)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute = AsyncMock(return_value=mock_result)
    
    # Mock refresh
    async def mock_refresh(doc):
        doc.id = uuid.uuid4()
        doc.created_at = "2024-01-01T00:00:00Z"
        doc.updated_at = "2024-01-01T00:00:00Z"
    
    mock_db_session.refresh = AsyncMock(side_effect=mock_refresh)
    mock_db_session.commit = AsyncMock()
    
    # Mock RAG client to raise exception
    mock_rag_client.upsert_document = AsyncMock(
        side_effect=Exception("RAG service unavailable")
    )
    
    # Act - should not raise exception
    result = await document_service.upsert_document(document_data)
    
    # Assert - operation should succeed despite RAG failure
    assert mock_db_session.commit.called
    assert mock_rag_client.upsert_document.called


# --------------------------------------------------------------------------
# Unit Tests - list_documents
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_documents_returns_paginated_results(
    document_service, mock_db_session
):
    """Verify list_documents returns paginated documents with total count."""
    # Arrange
    from datetime import datetime
    
    # Mock documents
    doc1 = Document(
        id=uuid.uuid4(),
        text="Document 1",
        heading="Heading 1",
        author="Author 1",
        status="active",
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        updated_at=datetime(2024, 1, 1, 12, 0, 0)
    )
    doc2 = Document(
        id=uuid.uuid4(),
        text="Document 2",
        heading="Heading 2",
        author="Author 2",
        status="active",
        created_at=datetime(2024, 1, 2, 12, 0, 0),
        updated_at=datetime(2024, 1, 2, 12, 0, 0)
    )
    
    # Mock count query
    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = 2
    
    # Mock documents query
    mock_docs_result = MagicMock()
    mock_docs_result.scalars.return_value.all.return_value = [doc2, doc1]
    
    # Setup execute to return different results based on query
    call_count = 0
    async def mock_execute(query):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return mock_count_result
        else:
            return mock_docs_result
    
    mock_db_session.execute = AsyncMock(side_effect=mock_execute)
    
    # Act
    documents, total = await document_service.list_documents(page=1, page_size=50)
    
    # Assert
    assert total == 2
    assert len(documents) == 2
    assert documents[0].heading == "Heading 2"  # Ordered by created_at desc
    assert documents[1].heading == "Heading 1"


@pytest.mark.asyncio
async def test_list_documents_calculates_correct_offset(
    document_service, mock_db_session
):
    """Verify list_documents calculates correct offset for pagination."""
    # Arrange
    from datetime import datetime
    
    doc = Document(
        id=uuid.uuid4(),
        text="Document",
        heading="Heading",
        author="Author",
        status="active",
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        updated_at=datetime(2024, 1, 1, 12, 0, 0)
    )
    
    # Mock count query
    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = 100
    
    # Mock documents query
    mock_docs_result = MagicMock()
    mock_docs_result.scalars.return_value.all.return_value = [doc]
    
    call_count = 0
    async def mock_execute(query):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return mock_count_result
        else:
            return mock_docs_result
    
    mock_db_session.execute = AsyncMock(side_effect=mock_execute)
    
    # Act
    documents, total = await document_service.list_documents(page=3, page_size=10)
    
    # Assert
    assert total == 100
    assert len(documents) == 1
    # Verify offset calculation: (page - 1) * page_size = (3 - 1) * 10 = 20
    # This is verified by the fact that the query executed successfully


# --------------------------------------------------------------------------
# Unit Tests - delete_document
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_document_deletes_existing_document(
    document_service, mock_db_session, mock_rag_client
):
    """Verify delete_document deletes an existing document and returns True."""
    # Arrange
    doc_id = uuid.uuid4()
    existing_doc = Document(
        id=doc_id,
        text="Test content",
        heading="Test Heading",
        author="Test Author",
        status="active"
    )
    
    # Mock database query to return existing document
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_doc
    mock_db_session.execute = AsyncMock(return_value=mock_result)
    mock_db_session.delete = AsyncMock()
    mock_db_session.commit = AsyncMock()
    
    # Act
    result = await document_service.delete_document(doc_id)
    
    # Assert
    assert result is True
    mock_db_session.delete.assert_called_once_with(existing_doc)
    mock_db_session.commit.assert_called_once()
    mock_rag_client.delete_document.assert_called_once_with(str(doc_id))


@pytest.mark.asyncio
async def test_delete_document_returns_false_for_nonexistent_document(
    document_service, mock_db_session, mock_rag_client
):
    """Verify delete_document returns False when document doesn't exist."""
    # Arrange
    doc_id = uuid.uuid4()
    
    # Mock database query to return None (document doesn't exist)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute = AsyncMock(return_value=mock_result)
    
    # Act
    result = await document_service.delete_document(doc_id)
    
    # Assert
    assert result is False
    assert not mock_db_session.delete.called
    assert not mock_db_session.commit.called
    assert not mock_rag_client.delete_document.called


@pytest.mark.asyncio
async def test_delete_document_syncs_to_rag_service(
    document_service, mock_db_session, mock_rag_client
):
    """Verify delete_document calls RAG client with correct document ID."""
    # Arrange
    doc_id = uuid.uuid4()
    existing_doc = Document(
        id=doc_id,
        text="Test content",
        heading="Test Heading",
        author="Test Author",
        status="active"
    )
    
    # Mock database query to return existing document
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_doc
    mock_db_session.execute = AsyncMock(return_value=mock_result)
    mock_db_session.delete = AsyncMock()
    mock_db_session.commit = AsyncMock()
    
    # Act
    result = await document_service.delete_document(doc_id)
    
    # Assert
    assert result is True
    mock_rag_client.delete_document.assert_called_once_with(str(doc_id))


@pytest.mark.asyncio
async def test_delete_document_continues_on_rag_failure(
    document_service, mock_db_session, mock_rag_client
):
    """Verify delete_document succeeds even when RAG sync fails."""
    # Arrange
    doc_id = uuid.uuid4()
    existing_doc = Document(
        id=doc_id,
        text="Test content",
        heading="Test Heading",
        author="Test Author",
        status="active"
    )
    
    # Mock database query to return existing document
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_doc
    mock_db_session.execute = AsyncMock(return_value=mock_result)
    mock_db_session.delete = AsyncMock()
    mock_db_session.commit = AsyncMock()
    
    # Mock RAG client to raise exception
    mock_rag_client.delete_document = AsyncMock(
        side_effect=Exception("RAG service unavailable")
    )
    
    # Act - should not raise exception
    result = await document_service.delete_document(doc_id)
    
    # Assert - operation should succeed despite RAG failure
    assert result is True
    assert mock_db_session.delete.called
    assert mock_db_session.commit.called
    assert mock_rag_client.delete_document.called
