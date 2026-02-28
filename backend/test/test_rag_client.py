"""
Unit tests for RAG client implementations.

Tests the HTTPRAGClient class with mocked httpx AsyncClient to verify
proper HTTP communication, timeout handling, and error handling.
"""
import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock
from infrastructure.rag.rag_client import HTTPRAGClient


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------

@pytest.fixture
def mock_httpx_client(mocker):
    """Mocks httpx.AsyncClient for testing HTTP calls."""
    mock_client = AsyncMock()
    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    return mock_client


@pytest.fixture
def rag_client(mock_httpx_client):
    """Creates an HTTPRAGClient instance with mocked httpx client."""
    return HTTPRAGClient(base_url="http://localhost:8082", timeout=10.0)


# --------------------------------------------------------------------------
# Unit Tests - HTTPRAGClient Initialization
# --------------------------------------------------------------------------

def test_http_rag_client_initialization():
    """Verify HTTPRAGClient initializes with correct base URL and timeout."""
    client = HTTPRAGClient(base_url="http://localhost:8082", timeout=5.0)
    assert client.base_url == "http://localhost:8082"
    assert client.timeout == 5.0


def test_http_rag_client_strips_trailing_slash():
    """Verify HTTPRAGClient strips trailing slash from base URL."""
    client = HTTPRAGClient(base_url="http://localhost:8082/", timeout=10.0)
    assert client.base_url == "http://localhost:8082"


# --------------------------------------------------------------------------
# Unit Tests - upsert_document
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_upsert_document_success(rag_client, mock_httpx_client):
    """Verify upsert_document sends correct POST request."""
    # Mock successful response
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_httpx_client.post = AsyncMock(return_value=mock_response)
    
    document_data = {
        "document": {
            "text": "Test document content",
            "heading": "Test Heading",
            "author": "Test Author",
            "original_id": "123e4567-e89b-12d3-a456-426614174000",
            "status": "active"
        },
        "namespace": "waterworks-department"
    }
    
    await rag_client.upsert_document(document_data)
    
    # Verify POST was called with correct URL and data
    mock_httpx_client.post.assert_called_once_with(
        "http://localhost:8082/documents/single",
        json=document_data
    )
    mock_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_upsert_document_http_error(rag_client, mock_httpx_client):
    """Verify upsert_document raises exception on HTTP error."""
    # Mock HTTP error response
    mock_httpx_client.post = AsyncMock(
        side_effect=httpx.HTTPStatusError(
            "404 Not Found",
            request=MagicMock(),
            response=MagicMock()
        )
    )
    
    document_data = {
        "document": {
            "text": "Test content",
            "heading": "Test",
            "author": "Author",
            "original_id": "123e4567-e89b-12d3-a456-426614174000",
            "status": "active"
        },
        "namespace": "waterworks-department"
    }
    
    with pytest.raises(httpx.HTTPStatusError):
        await rag_client.upsert_document(document_data)


@pytest.mark.asyncio
async def test_upsert_document_timeout(rag_client, mock_httpx_client):
    """Verify upsert_document raises exception on timeout."""
    # Mock timeout exception
    mock_httpx_client.post = AsyncMock(
        side_effect=httpx.TimeoutException("Request timed out")
    )
    
    document_data = {
        "document": {
            "text": "Test content",
            "heading": "Test",
            "author": "Author",
            "original_id": "123e4567-e89b-12d3-a456-426614174000",
            "status": "active"
        },
        "namespace": "waterworks-department"
    }
    
    with pytest.raises(httpx.TimeoutException):
        await rag_client.upsert_document(document_data)


# --------------------------------------------------------------------------
# Unit Tests - delete_document
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_document_success(rag_client, mock_httpx_client):
    """Verify delete_document sends correct DELETE request."""
    # Mock successful response
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_httpx_client.delete = AsyncMock(return_value=mock_response)
    
    document_id = "123e4567-e89b-12d3-a456-426614174000"
    
    await rag_client.delete_document(document_id)
    
    # Verify DELETE was called with correct URL
    mock_httpx_client.delete.assert_called_once_with(
        f"http://localhost:8082/documents/{document_id}"
    )
    mock_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_delete_document_http_error(rag_client, mock_httpx_client):
    """Verify delete_document raises exception on HTTP error."""
    # Mock HTTP error response
    mock_httpx_client.delete = AsyncMock(
        side_effect=httpx.HTTPStatusError(
            "404 Not Found",
            request=MagicMock(),
            response=MagicMock()
        )
    )
    
    document_id = "123e4567-e89b-12d3-a456-426614174000"
    
    with pytest.raises(httpx.HTTPStatusError):
        await rag_client.delete_document(document_id)


@pytest.mark.asyncio
async def test_delete_document_timeout(rag_client, mock_httpx_client):
    """Verify delete_document raises exception on timeout."""
    # Mock timeout exception
    mock_httpx_client.delete = AsyncMock(
        side_effect=httpx.TimeoutException("Request timed out")
    )
    
    document_id = "123e4567-e89b-12d3-a456-426614174000"
    
    with pytest.raises(httpx.TimeoutException):
        await rag_client.delete_document(document_id)


# --------------------------------------------------------------------------
# Unit Tests - close
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_close_client(rag_client, mock_httpx_client):
    """Verify close method properly closes the httpx client."""
    mock_httpx_client.aclose = AsyncMock()
    
    await rag_client.close()
    
    mock_httpx_client.aclose.assert_called_once()


# --------------------------------------------------------------------------
# Unit Tests - Error Handling
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_upsert_document_unexpected_error(rag_client, mock_httpx_client):
    """Verify upsert_document handles unexpected exceptions."""
    # Mock unexpected exception
    mock_httpx_client.post = AsyncMock(
        side_effect=Exception("Unexpected error")
    )
    
    document_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "text": "Test content",
        "heading": "Test",
        "author": "Author",
        "status": "active"
    }
    
    with pytest.raises(Exception) as exc_info:
        await rag_client.upsert_document(document_data)
    
    assert "Unexpected error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_delete_document_unexpected_error(rag_client, mock_httpx_client):
    """Verify delete_document handles unexpected exceptions."""
    # Mock unexpected exception
    mock_httpx_client.delete = AsyncMock(
        side_effect=Exception("Unexpected error")
    )
    
    document_id = "123e4567-e89b-12d3-a456-426614174000"
    
    with pytest.raises(Exception) as exc_info:
        await rag_client.delete_document(document_id)
    
    assert "Unexpected error" in str(exc_info.value)



# --------------------------------------------------------------------------
# Unit Tests - GRPCRAGClient (Placeholder)
# --------------------------------------------------------------------------

from infrastructure.rag.rag_client import GRPCRAGClient


def test_grpc_rag_client_initialization():
    """Verify GRPCRAGClient initializes with correct gRPC address."""
    client = GRPCRAGClient(grpc_address="localhost:8082")
    assert client.grpc_address == "localhost:8082"


@pytest.mark.asyncio
async def test_grpc_upsert_document_not_implemented():
    """Verify GRPCRAGClient.upsert_document raises NotImplementedError."""
    client = GRPCRAGClient(grpc_address="localhost:8082")
    
    document_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "text": "Test document content",
        "heading": "Test Heading",
        "author": "Test Author",
        "status": "active"
    }
    
    with pytest.raises(NotImplementedError) as exc_info:
        await client.upsert_document(document_data)
    
    assert "gRPC RAG client is not yet implemented" in str(exc_info.value)


@pytest.mark.asyncio
async def test_grpc_delete_document_not_implemented():
    """Verify GRPCRAGClient.delete_document raises NotImplementedError."""
    client = GRPCRAGClient(grpc_address="localhost:8082")
    
    document_id = "123e4567-e89b-12d3-a456-426614174000"
    
    with pytest.raises(NotImplementedError) as exc_info:
        await client.delete_document(document_id)
    
    assert "gRPC RAG client is not yet implemented" in str(exc_info.value)


@pytest.mark.asyncio
async def test_grpc_close_placeholder():
    """Verify GRPCRAGClient.close executes without error (placeholder)."""
    client = GRPCRAGClient(grpc_address="localhost:8082")
    
    # Should not raise any exception
    await client.close()


# --------------------------------------------------------------------------
# Unit Tests - RAG Client Factory
# --------------------------------------------------------------------------

from infrastructure.rag import get_rag_client
from unittest.mock import patch


def test_get_rag_client_http_protocol():
    """Verify get_rag_client returns HTTPRAGClient when protocol is 'http'."""
    with patch("infrastructure.rag.settings") as mock_settings:
        mock_settings.RAG_PROTOCOL = "http"
        mock_settings.RAG_SERVICE_URL = "http://localhost:8082"
        
        # Reset singleton
        import infrastructure.rag
        infrastructure.rag._rag_client_instance = None
        
        client = get_rag_client()
        
        assert isinstance(client, HTTPRAGClient)
        assert client.base_url == "http://localhost:8082"


def test_get_rag_client_grpc_protocol():
    """Verify get_rag_client returns GRPCRAGClient when protocol is 'grpc'."""
    with patch("infrastructure.rag.settings") as mock_settings:
        mock_settings.RAG_PROTOCOL = "grpc"
        mock_settings.RAG_GRPC_ADDRESS = "localhost:8082"
        
        # Reset singleton
        import infrastructure.rag
        infrastructure.rag._rag_client_instance = None
        
        client = get_rag_client()
        
        assert isinstance(client, GRPCRAGClient)
        assert client.grpc_address == "localhost:8082"


def test_get_rag_client_default_to_http():
    """Verify get_rag_client defaults to HTTPRAGClient for unknown protocol."""
    with patch("infrastructure.rag.settings") as mock_settings:
        mock_settings.RAG_PROTOCOL = "unknown"
        mock_settings.RAG_SERVICE_URL = "http://localhost:8082"
        
        # Reset singleton
        import infrastructure.rag
        infrastructure.rag._rag_client_instance = None
        
        client = get_rag_client()
        
        assert isinstance(client, HTTPRAGClient)


def test_get_rag_client_singleton_pattern():
    """Verify get_rag_client returns the same instance on multiple calls."""
    with patch("infrastructure.rag.settings") as mock_settings:
        mock_settings.RAG_PROTOCOL = "http"
        mock_settings.RAG_SERVICE_URL = "http://localhost:8082"
        
        # Reset singleton
        import infrastructure.rag
        infrastructure.rag._rag_client_instance = None
        
        client1 = get_rag_client()
        client2 = get_rag_client()
        
        assert client1 is client2


def test_get_rag_client_case_insensitive_protocol():
    """Verify get_rag_client handles protocol case-insensitively."""
    with patch("infrastructure.rag.settings") as mock_settings:
        mock_settings.RAG_PROTOCOL = "GRPC"
        mock_settings.RAG_GRPC_ADDRESS = "localhost:8082"
        
        # Reset singleton
        import infrastructure.rag
        infrastructure.rag._rag_client_instance = None
        
        client = get_rag_client()
        
        assert isinstance(client, GRPCRAGClient)
