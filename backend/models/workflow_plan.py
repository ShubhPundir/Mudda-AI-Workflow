"""
WorkflowPlan model for generated workflow plans
"""
from sqlalchemy import Column, String, Text, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from .base import Base


class WorkflowPlan(Base):
    """Model for generated workflow plans"""
    __tablename__ = "workflow_plans"
    __table_args__ = {'schema': 'workflow'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid())
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    issue_id = Column(UUID(as_uuid=True), nullable=True)
    plan_json = Column(JSONB, nullable=False)
    ai_model_used = Column(Text, nullable=True)
    status = Column(Text, nullable=True, default="DRAFT")  # draft, active, completed, failed
    created_by = Column(Text, nullable=True)
    approved_by = Column(Text, nullable=True)
    approval_notes = Column(Text, nullable=True)
    version = Column(Text, nullable=True, default="1.0")
    is_temporal_ready = Column(Boolean, nullable=True, default=False)
    created_at = Column(DateTime(timezone=False), nullable=True, default=func.now())
    updated_at = Column(DateTime(timezone=False), nullable=True, default=func.now(), onupdate=func.now())
