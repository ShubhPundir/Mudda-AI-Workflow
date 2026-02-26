from sqlalchemy import Column, String, Text, DateTime, Boolean, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from .base import Base


"""
Component model matching the actual database schema
"""
class Component(Base):
    """
    Component model representing a business-level logical unit.
    Each component wraps one or more activities, orchestrates them,
    and provides configuration for retries, logging, and metrics.
    """
    __tablename__ = "components"
    __table_args__ = {'schema': 'workflow'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid())

    # Metadata
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Text, nullable=True)  # e.g., "Home Services", "Gov Notifications"
    owner_service = Column(Text, nullable=True)
    version = Column(String(20), nullable=True, default='1.0')
    is_active = Column(Boolean, nullable=False, default=True)

    # Activities definition
    # List of activity names and config this component orchestrates
    # Example:
    # [
    #   {"activity_name": "llm_activity", "retry_policy": {...}, "metadata": {...}},
    #   {"activity_name": "plumber_dispatch_activity", "retry_policy": {...}, "metadata": {...}},
    #   {"activity_name": "human_feedback_activity", "retry_policy": {...}}
    # ]
    activities = Column(JSONB, nullable=False, default=list)

    # Optional global component-level configuration
    config = Column(JSONB, nullable=True, default={})

    # Audit info
    created_at = Column(DateTime(timezone=True), nullable=True, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, default=func.now(), onupdate=func.now())
