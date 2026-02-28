"""
RAG Client abstract interface for document synchronization.

This module defines the abstract interface for communicating with the RAG service.
Concrete implementations can use HTTP REST or gRPC protocols.
"""
from abc import ABC, abstractmethod
from typing import Dict
from schemas.rag_schema import RAGUpsertRequest


class RAGClient(ABC):
    """
    Abstract base class for RAG service clients.
    
    This interface defines the contract for synchronizing document operations
    with the RAG (Retrieval-Augmented Generation) service. Implementations
    should handle protocol-specific communication (HTTP, gRPC, etc.).
    """
    
    @abstractmethod
    async def upsert_document(self, request: RAGUpsertRequest) -> None:
        """
        Upsert a document in the RAG service.
        
        Sends document data to the RAG service for indexing. This operation
        should create a new document if it doesn't exist or update an existing
        document based on the document ID.
        
        Args:
            request: RAGUpsertRequest containing document data and namespace
        
        Raises:
            Exception: If the RAG service communication fails
        """
        pass
    
    @abstractmethod
    async def delete_document(self, document_id: str) -> None:
        """
        Delete a document from the RAG service.
        
        Sends a delete request to the RAG service to remove the document
        from the index.
        
        Args:
            document_id: Document UUID as string
        
        Raises:
            Exception: If the RAG service communication fails
        """
        pass


import httpx
import logging

logger = logging.getLogger(__name__)


class HTTPRAGClient(RAGClient):
    """
    HTTP REST implementation of the RAG client.
    
    This client uses httpx AsyncClient to communicate with the RAG service
    over HTTP REST protocol. It handles timeouts and provides proper error
    handling for network failures.
    """
    
    def __init__(self, base_url: str, timeout: float = 10.0):
        """
        Initialize the HTTP RAG client.
        
        Args:
            base_url: Base URL of the RAG service (e.g., "http://localhost:8082")
            timeout: Request timeout in seconds (default: 10.0)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def upsert_document(self, request: RAGUpsertRequest) -> None:
        """
        Upsert a document in the RAG service via HTTP POST.
        
        Sends a POST request to /documents/single with the document data.
        The request body follows the schema defined in RAGUpsertRequest.
        
        Args:
            request: RAGUpsertRequest containing document data and namespace
        
        Raises:
            httpx.HTTPError: If the HTTP request fails
            httpx.TimeoutException: If the request times out
        """
        url = f"{self.base_url}/documents/single"
        try:
            # Convert Pydantic model to dict for JSON serialization
            payload = request.model_dump()
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            logger.debug(f"Successfully upserted document {request.document.original_id} to RAG service")
        except httpx.HTTPError as e:
            logger.error(f"HTTP error upserting document to RAG service: {e}")
            raise
        except httpx.TimeoutException as e:
            logger.error(f"Timeout upserting document to RAG service: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error upserting document to RAG service: {e}")
            raise
    
    async def delete_document(self, document_id: str) -> None:
        """
        Delete a document from the RAG service via HTTP DELETE.
        
        Sends a DELETE request to /documents/{document_id}.
        
        Args:
            document_id: Document UUID as string
        
        Raises:
            httpx.HTTPError: If the HTTP request fails
            httpx.TimeoutException: If the request times out
        """
        url = f"{self.base_url}/documents/{document_id}"
        try:
            response = await self.client.delete(url)
            response.raise_for_status()
            logger.debug(f"Successfully deleted document {document_id} from RAG service")
        except httpx.HTTPError as e:
            logger.error(f"HTTP error deleting document from RAG service: {e}")
            raise
        except httpx.TimeoutException as e:
            logger.error(f"Timeout deleting document from RAG service: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting document from RAG service: {e}")
            raise
    
    async def close(self):
        """
        Close the HTTP client and release resources.
        
        Should be called when the client is no longer needed to properly
        clean up connections.
        """
        await self.client.aclose()
        logger.debug("HTTP RAG client closed")


class GRPCRAGClient(RAGClient):
    """
    gRPC implementation of the RAG client (placeholder).
    
    This client is a placeholder for future gRPC implementation. When implemented,
    it will use gRPC protocol to communicate with the RAG service for better
    performance and type safety compared to HTTP REST.
    
    TODO: Implement gRPC communication using grpcio library
    - Define protobuf schema for document messages
    - Generate Python gRPC stubs from .proto files
    - Initialize gRPC channel and stub in __init__
    - Implement upsert_document using gRPC UpsertDocument RPC
    - Implement delete_document using gRPC DeleteDocument RPC
    - Add proper error handling for gRPC status codes
    - Add connection pooling and retry logic
    """
    
    def __init__(self, grpc_address: str):
        """
        Initialize the gRPC RAG client.
        
        Args:
            grpc_address: gRPC server address (e.g., "localhost:8082")
        
        TODO: Initialize gRPC channel and stub
        - Create grpc.aio.insecure_channel(grpc_address)
        - Initialize RAGServiceStub from generated protobuf code
        - Configure channel options (keepalive, compression, etc.)
        """
        self.grpc_address = grpc_address
        # TODO: self.channel = grpc.aio.insecure_channel(grpc_address)
        # TODO: self.stub = rag_service_pb2_grpc.RAGServiceStub(self.channel)
        logger.info(f"GRPCRAGClient initialized for address: {grpc_address} (placeholder)")
    
    async def upsert_document(self, request: RAGUpsertRequest) -> None:
        """
        Upsert a document in the RAG service via gRPC (placeholder).
        
        Args:
            request: RAGUpsertRequest containing document data and namespace
        
        TODO: Implement gRPC upsert call
        - Convert RAGUpsertRequest to protobuf UpsertDocumentRequest message
        - Call self.stub.UpsertDocument(request)
        - Handle gRPC exceptions (grpc.RpcError)
        - Map gRPC status codes to appropriate exceptions
        
        Raises:
            NotImplementedError: This is a placeholder implementation
        """
        logger.warning(f"GRPCRAGClient.upsert_document called but not implemented (document_id: {request.document.original_id})")
        # TODO: Implement actual gRPC call
        # grpc_request = rag_service_pb2.UpsertDocumentRequest(
        #     document=rag_service_pb2.Document(
        #         text=request.document.text,
        #         heading=request.document.heading,
        #         author=request.document.author,
        #         original_id=request.document.original_id,
        #         status=request.document.status
        #     ),
        #     namespace=request.namespace
        # )
        # response = await self.stub.UpsertDocument(grpc_request)
        raise NotImplementedError("gRPC RAG client is not yet implemented")
    
    async def delete_document(self, document_id: str) -> None:
        """
        Delete a document from the RAG service via gRPC (placeholder).
        
        Args:
            document_id: Document UUID as string
        
        TODO: Implement gRPC delete call
        - Create protobuf DeleteDocumentRequest message with document_id
        - Call self.stub.DeleteDocument(request)
        - Handle gRPC exceptions (grpc.RpcError)
        - Map gRPC status codes to appropriate exceptions
        
        Raises:
            NotImplementedError: This is a placeholder implementation
        """
        logger.warning(f"GRPCRAGClient.delete_document called but not implemented (document_id: {document_id})")
        # TODO: Implement actual gRPC call
        # request = rag_service_pb2.DeleteDocumentRequest(id=document_id)
        # response = await self.stub.DeleteDocument(request)
        raise NotImplementedError("gRPC RAG client is not yet implemented")
    
    async def close(self):
        """
        Close the gRPC channel and release resources (placeholder).
        
        TODO: Implement channel cleanup
        - Call await self.channel.close()
        - Wait for channel to be properly closed
        """
        logger.debug("GRPCRAGClient.close called (placeholder)")
        # TODO: await self.channel.close()
        pass
