"""
Document model for document CRUD service
"""
from sqlalchemy import Column, String, Text, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from .base import Base


class Document(Base):
    """
    Document entity for storing text documents with metadata.
    
    Attributes:
        id: Unique document identifier (UUID)
        text: Document text content
        heading: Document heading/title
        author: Document author name
        status: Document status (default: 'active')
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text = Column(Text, nullable=False)
    heading = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="active")
    namespace = Column(String(50), nullable=False, default="waterworks-department")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_documents_namespace', 'namespace'),
        Index('idx_documents_created_at', 'created_at'),
        {'schema': 'workflow'}
    )
