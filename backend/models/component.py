from sqlalchemy import Column, String, Text, DateTime, Boolean, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from .base import Base


"""
Component model matching the actual database schema
"""
class Component(Base):
    """Model for available API components in the system"""
    __tablename__ = "components"
    __table_args__ = {'schema': 'workflow'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid())
    
    # Metadata
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(
        String(50), 
        CheckConstraint("type IN ('REST', 'RPC', 'GraphQL')"),
        nullable=False
    )
    category = Column(Text, nullable=True)
    
    # Endpoint details
    endpoint_url = Column(Text, nullable=False)
    http_method = Column(
        String(10),
        CheckConstraint("http_method IN ('GET', 'POST', 'PUT', 'PATCH', 'DELETE')"),
        nullable=True
    )
    
    # Optional GraphQL or RPC specific fields
    query_template = Column(Text, nullable=True)
    rpc_function = Column(Text, nullable=True)
    
    # Authentication info
    auth_type = Column(
        String(20),
        CheckConstraint("auth_type IN ('NONE', 'API_KEY', 'BEARER', 'BASIC', 'OAUTH2')"),
        nullable=True,
        default='NONE'
    )
    auth_config = Column(JSONB, nullable=True, default={})
    
    # Schema definitions
    request_schema = Column(JSONB, nullable=True, default={})
    response_schema = Column(JSONB, nullable=True, default={})
    path_params = Column(JSONB, nullable=True, default={})
    query_params = Column(JSONB, nullable=True, default={})
    
    # Versioning and ownership
    version = Column(String(20), nullable=True, default='1.0')
    owner_service = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=True, default=True)
    
    # Audit info
    created_at = Column(DateTime(timezone=True), nullable=True, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, default=func.now(), onupdate=func.now())
