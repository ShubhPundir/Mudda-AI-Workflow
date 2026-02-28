"""
Document Service Module

This module provides the business logic layer for document CRUD operations.
It handles document creation, retrieval, updates, deletion, and synchronization
with the RAG (Retrieval-Augmented Generation) service.
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.rag.rag_client import RAGClient

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Service class for managing document operations.
    
    This service handles all document-related business logic including:
    - Creating and updating documents (upsert)
    - Retrieving documents by ID
    - Listing documents with pagination
    - Deleting documents
    - Synchronizing document changes with the RAG service
    
    The service ensures that RAG synchronization failures do not affect
    the primary CRUD operations, providing graceful degradation.
    """
    
    def __init__(self, db: AsyncSession, rag_client: RAGClient):
        """
        Initialize the DocumentService.
        
        Args:
            db: SQLAlchemy async database session for executing queries
            rag_client: RAG client instance for synchronizing document changes
        """
        self.db = db
        self.rag_client = rag_client
        logger.debug("DocumentService initialized")

    async def upsert_document(self, document_data: 'DocumentCreate') -> 'DocumentResponse':
        """
        Create a new document or update an existing one.
        
        This method implements the upsert operation:
        - If document_data.id is None, generates a new UUID and creates a new document
        - If document_data.id exists in the database, updates the existing document
        - If document_data.id is provided but doesn't exist, creates a new document with that ID
        
        After the database operation, synchronizes the document with the RAG service.
        RAG synchronization failures are logged but do not fail the operation.
        
        Args:
            document_data: DocumentCreate schema with document fields
            
        Returns:
            DocumentResponse with the created/updated document data
            
        Raises:
            Exception: If database operation fails
        """
        from sqlalchemy import select
        from models.document import Document
        from schemas.document_schema import DocumentResponse
        import uuid
        
        # Generate UUID if not provided
        doc_id = document_data.id or uuid.uuid4()
        
        # Check if document exists by ID
        result = await self.db.execute(select(Document).where(Document.id == doc_id))
        existing_doc = result.scalar_one_or_none()
        
        if existing_doc:
            # Update existing document
            logger.debug(f"Updating existing document with ID: {doc_id}")
            for key, value in document_data.model_dump(exclude_unset=True, exclude={'id'}).items():
                setattr(existing_doc, key, value)
            document = existing_doc
        else:
            # Insert new document
            logger.debug(f"Creating new document with ID: {doc_id}")
            document = Document(
                id=doc_id,
                **document_data.model_dump(exclude={'id'})
            )
            self.db.add(document)
        
        # Commit transaction and refresh document
        await self.db.commit()
        await self.db.refresh(document)
        
        # Call _sync_to_rag_upsert helper
        await self._sync_to_rag_upsert(document)
        
        # Return DocumentResponse
        return DocumentResponse.model_validate(document)

    async def get_document(self, document_id: 'uuid.UUID') -> 'Optional[DocumentResponse]':
        """
        Retrieve a document by its ID.

        Queries the database for a document with the specified ID and returns
        the document data if found, or None if the document does not exist.

        Args:
            document_id: UUID of the document to retrieve

        Returns:
            DocumentResponse with the document data if found, None otherwise

        Raises:
            Exception: If database query fails
        """
        from sqlalchemy import select
        from models.document import Document
        from schemas.document_schema import DocumentResponse
        from typing import Optional
        import uuid

        logger.debug(f"Retrieving document with ID: {document_id}")

        # Query document by ID using async select
        result = await self.db.execute(select(Document).where(Document.id == document_id))
        document = result.scalar_one_or_none()

        # Return DocumentResponse or None if not found
        if document:
            logger.debug(f"Document {document_id} found")
            return DocumentResponse.model_validate(document)
        else:
            logger.debug(f"Document {document_id} not found")
            return None

    async def list_documents(self, page: int = 1, page_size: int = 50) -> tuple[list['DocumentResponse'], int]:
        """
        Retrieve a paginated list of documents.

        Queries the database for documents with pagination support, ordered by
        creation date (newest first). Returns both the list of documents for the
        requested page and the total count of all documents.

        Args:
            page: Page number (1-indexed, default: 1)
            page_size: Number of documents per page (default: 50)

        Returns:
            Tuple containing:
                - List of DocumentResponse objects for the requested page
                - Total count of all documents in the database

        Raises:
            Exception: If database query fails
        """
        from sqlalchemy import select, func
        from models.document import Document
        from schemas.document_schema import DocumentResponse

        logger.debug(f"Listing documents: page={page}, page_size={page_size}")

        # Query total document count
        count_result = await self.db.execute(select(func.count(Document.id)))
        total = count_result.scalar()

        # Calculate offset from page and page_size
        offset = (page - 1) * page_size

        # Query paginated documents ordered by created_at desc
        result = await self.db.execute(
            select(Document)
            .order_by(Document.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        documents = result.scalars().all()

        # Return list of DocumentResponse and total count
        logger.debug(f"Found {len(documents)} documents on page {page}, total: {total}")
        return [DocumentResponse.model_validate(doc) for doc in documents], total


    async def delete_document(self, document_id: 'uuid.UUID') -> bool:
        """
        Delete a document by its ID.

        Queries the database for a document with the specified ID and deletes it
        if found. After successful deletion, synchronizes the deletion with the
        RAG service. RAG synchronization failures are logged but do not fail the operation.

        Args:
            document_id: UUID of the document to delete

        Returns:
            True if the document was found and deleted, False if not found

        Raises:
            Exception: If database operation fails
        """
        from sqlalchemy import select
        from models.document import Document
        import uuid

        logger.debug(f"Deleting document with ID: {document_id}")

        # Query document by ID
        result = await self.db.execute(select(Document).where(Document.id == document_id))
        document = result.scalar_one_or_none()

        # Return False if not found
        if not document:
            logger.debug(f"Document {document_id} not found for deletion")
            return False

        # Delete document and commit transaction
        await self.db.delete(document)
        await self.db.commit()
        logger.info(f"Successfully deleted document {document_id}")

        # Call _sync_to_rag_delete helper
        await self._sync_to_rag_delete(document_id)

        # Return True on success
        return True

    async def _sync_to_rag_upsert(self, document: 'Document'):
        """
        Synchronize document upsert to RAG service.
        
        This helper method sends the document data to the RAG service for indexing.
        Any errors during synchronization are logged but do not fail the operation,
        ensuring graceful degradation when the RAG service is unavailable.
        
        Args:
            document: Document model instance to synchronize
        """
        try:
            await self.rag_client.upsert_document({
                "id": str(document.id),
                "text": document.text,
                "heading": document.heading,
                "author": document.author,
                "status": document.status
            })
            logger.info(f"Successfully synchronized document {document.id} to RAG service")
        except Exception as e:
            logger.error(f"Failed to sync document {document.id} to RAG service: {e}")

    async def _sync_to_rag_delete(self, document_id: 'uuid.UUID'):
        """
        Synchronize document deletion to RAG service.
        
        This helper method sends a delete request to the RAG service to remove
        the document from the index. Any errors during synchronization are logged
        but do not fail the operation, ensuring graceful degradation when the RAG
        service is unavailable.
        
        Args:
            document_id: UUID of the document to delete from RAG service
        """
        try:
            await self.rag_client.delete_document(str(document_id))
            logger.info(f"Successfully synchronized document deletion {document_id} to RAG service")
        except Exception as e:
            logger.error(f"Failed to delete document {document_id} from RAG service: {e}")
