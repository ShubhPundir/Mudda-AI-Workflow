"""
WorkflowPlan model for generated workflow plans
"""
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from .base import Base


class WorkflowPlan(Base):
    """Model for generated workflow plans"""
    __tablename__ = "workflow_plans"
    __table_args__ = {'schema': 'workflow'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid())
    workflow_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    problem_statement = Column(Text, nullable=False)
    workflow_json = Column(JSONB, nullable=False)
    status = Column(String(50), nullable=True, default="draft")  # draft, active, completed, failed
    created_at = Column(DateTime(timezone=True), nullable=True, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, default=func.now(), onupdate=func.now())
