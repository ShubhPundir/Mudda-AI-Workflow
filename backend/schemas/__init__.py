"""
Schemas package for Mudda AI Workflow system
"""
from .workflow_schema import (
    WorkflowStepSchema,
    WorkflowPlanSchema,
    ProblemStatementRequest,
    WorkflowGenerationResponse,
    WorkflowExecutionRequest,
    WorkflowExecutionResponse
)
from .ai_schemas import (
    ActivitySelectionResponse,
    WorkflowPlanResponse,
    WorkflowStep
)
from .document_schema import (
    DocumentBase,
    DocumentCreate,
    DocumentResponse,
    DocumentListResponse
)
from .rag_schema import (
    RAGDocumentData,
    RAGUpsertRequest,
    RAGDeleteRequest
)
from .activity_schemas import (
    # Document Activities
    PDFServiceInput,
    PDFServiceOutput,
    # Execution Tracking Activities
    UpdateExecutionStatusInput,
    UpdateExecutionStatusOutput,
    # External Service Activities
    
    # Human Signals

    # Issue Activities
    UpdateIssueInput,
    UpdateIssueOutput,
    FetchIssueDetailsInput,
    FetchIssueDetailsOutput,
    
    # Notification Activities
    SendNotificationInput,
    SendNotificationOutput,
)

__all__ = [
    # Workflow schemas
    "WorkflowStepSchema",
    "WorkflowPlanSchema",
    "ProblemStatementRequest",
    "WorkflowGenerationResponse",
    "WorkflowExecutionRequest",
    "WorkflowExecutionResponse",
    # AI schemas
    "ActivitySelectionResponse",
    "WorkflowPlanResponse",
    "WorkflowStep",
    # Document schemas
    "DocumentBase",
    "DocumentCreate",
    "DocumentResponse",
    "DocumentListResponse",
    # RAG schemas
    "RAGDocumentData",
    "RAGUpsertRequest",
    "RAGDeleteRequest",
    # Activity schemas - Document
    "PDFServiceInput",
    "PDFServiceOutput",
    # Activity schemas - Execution Tracking
    "UpdateExecutionStatusInput",
    "UpdateExecutionStatusOutput",
    # Activity schemas - External Services

    # Activity schemas - Human

    # Activity schemas - Issue
    "UpdateIssueInput",
    "UpdateIssueOutput",
    "FetchIssueDetailsInput",
    "FetchIssueDetailsOutput",
    # Activity schemas - Notification
    "SendNotificationInput",
    "SendNotificationOutput",
]