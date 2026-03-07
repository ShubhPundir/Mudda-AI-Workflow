"""
RAG Client Factory Module

This module provides a factory function for creating RAG client instances
based on configuration settings. It supports both HTTP REST and gRPC protocols
for communicating with the RAG service.
"""
from config import settings
from .rag_client import RAGClient, HTTPRAGClient, GRPCRAGClient


_rag_client_instance = None


def get_rag_client() -> RAGClient:
    """
    Factory function to get or create a RAG client instance.
    
    This function implements a singleton pattern to ensure only one RAG client
    instance is created per application lifecycle. The client type (HTTP or gRPC)
    is determined by the RAG_PROTOCOL configuration setting.
    
    Returns:
        RAGClient: An instance of HTTPRAGClient or GRPCRAGClient based on configuration
    
    Configuration:
        - RAG_PROTOCOL: Protocol to use ("http" or "grpc")
        - RAG_SERVICE_URL: Base URL for HTTP client (e.g., "http://localhost:8082")
        - RAG_GRPC_ADDRESS: gRPC server address (e.g., "localhost:8082")
    
    Examples:
        >>> # In FastAPI dependency injection
        >>> def get_document_service(
        ...     db: AsyncSession = Depends(get_db),
        ...     rag_client: RAGClient = Depends(get_rag_client)
        ... ) -> DocumentService:
        ...     return DocumentService(db, rag_client)
    """
    global _rag_client_instance
    
    if _rag_client_instance is None:
        if settings.RAG_PROTOCOL.lower() == "grpc":
            _rag_client_instance = GRPCRAGClient(settings.RAG_GRPC_ADDRESS)
        else:
            # Default to HTTP if protocol is not recognized or is "http"
            _rag_client_instance = HTTPRAGClient(settings.RAG_SERVICE_URL)
    
    return _rag_client_instance


__all__ = ["get_rag_client", "RAGClient", "HTTPRAGClient", "GRPCRAGClient"]
