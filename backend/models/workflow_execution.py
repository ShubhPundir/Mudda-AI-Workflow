"""
WorkflowExecution model for tracking workflow executions
"""
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from .base import Base


class WorkflowExecution(Base):
    """Model for tracking workflow executions"""
    __tablename__ = "workflow_executions"
    __table_args__ = {'schema': 'workflow'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid())
    workflow_plan_id = Column(UUID(as_uuid=True), nullable=False)
    temporal_workflow_id = Column(String(255), nullable=True)
    status = Column(String(50), nullable=True, default="pending")  # pending, running, completed, failed
    execution_data = Column(JSONB, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, default=func.now())
