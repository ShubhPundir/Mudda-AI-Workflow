import enum
from sqlalchemy import Column, String, Text, DateTime, Boolean, Float, BigInteger, Enum, Sequence
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from .base import Base

class IssueStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    REJECTED = "REJECTED"

class Issue(Base):
    """
    Issue model representing a civic issue reported by a user.
    Matches the schema defined in the Java entity.
    """
    __tablename__ = "issues"
    __table_args__ = {'schema': 'public'}

    # PK with sequence
    id = Column(
        BigInteger, 
        Sequence('issues_id_seq'), 
        primary_key=True, 
        name="issue_id"
    )

    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(
        Enum(IssueStatus), 
        name="issue_status", 
        nullable=False, 
        default=IssueStatus.OPEN
    )

    # Foreign Keys (as BigInteger as per Java entity)
    user_id = Column(BigInteger, nullable=False)
    location_id = Column(BigInteger, nullable=False)
    category_id = Column(BigInteger, name="issue_category_id", nullable=False)

    # PG Array for media URLs
    media_urls = Column(ARRAY(Text), name="media_urls", nullable=True)

    # Flags
    delete_flag = Column(Boolean, nullable=False, default=False)
    urgency_flag = Column(Boolean, nullable=False, default=False)
    
    # Scores
    severity_score = Column(Float, nullable=False, default=0.0)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True), 
        nullable=True, 
        onupdate=func.now(),
        server_default=func.now()
    )

    def __repr__(self):
        return f"<Issue(id={self.id}, title='{self.title}', status='{self.status}')>"
