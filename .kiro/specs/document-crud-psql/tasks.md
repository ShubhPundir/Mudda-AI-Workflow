# Implementation Plan: Document CRUD Service with RAG Synchronization

## Overview

This implementation plan breaks down the document CRUD service into incremental coding tasks. Each task builds on previous work, starting with the data layer, then service layer, API layer, and finally integration with the RAG service. The plan includes property-based tests and unit tests as sub-tasks to validate functionality early.

## Tasks

- [x] 1. Set up document data model and database schema
  - Create Document SQLAlchemy model in backend/models/document.py
  - Define all columns: id (UUID), text, heading, author, status, created_at, updated_at
  - Add indexes for status and created_at fields
  - Update backend/models/__init__.py to export Document model
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Create Pydantic schemas for request/response validation
  - Create backend/schemas/document_schema.py
  - Define DocumentBase, DocumentCreate, DocumentResponse, DocumentListResponse schemas
  - Add field validation (min_length, max_length) for text, heading, author
  - Update backend/schemas/__init__.py to export document schemas
  - _Requirements: 2.1, 2.5, 6.1_

- [ ] 3. Implement RAG client infrastructure
  - [x] 3.1 Create RAG client abstract interface
    - Create backend/infrastructure/rag/rag_client.py
    - Define RAGClient abstract base class with upsert_document and delete_document methods
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  
  - [x] 3.2 Implement HTTP RAG client
    - Implement HTTPRAGClient class using httpx AsyncClient
    - Add upsert_document method (POST to /documents/upsert)
    - Add delete_document method (DELETE to /documents/{id})
    - Add proper timeout and error handling
    - _Requirements: 5.1, 5.2, 5.4_
  
  - [x] 3.3 Implement gRPC RAG client stub
    - Implement GRPCRAGClient class with placeholder methods
    - Add comments indicating where gRPC implementation would go
    - _Requirements: 5.3_
  
  - [x] 3.4 Create RAG client factory
    - Create backend/infrastructure/rag/__init__.py
    - Implement get_rag_client() factory function
    - Add protocol selection logic (HTTP vs gRPC based on config)
    - _Requirements: 5.3, 5.4_

- [x] 4. Update configuration for RAG service settings
  - Add RAG_SERVICE_URL, RAG_PROTOCOL, RAG_GRPC_ADDRESS to Settings class in backend/config.py
  - Set default values (http://localhost:8082, "http", "localhost:8082")
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 5. Implement document service layer
  - [x] 5.1 Create DocumentService class
    - Create backend/services/document_service.py
    - Implement __init__ method accepting db session and rag_client
    - Add logging configuration
    - _Requirements: 2.1, 2.2, 2.3, 3.1, 4.1_
  
  - [x] 5.2 Implement upsert_document method
    - Add logic to check if document exists by ID
    - Generate UUID if ID not provided
    - Insert new document or update existing document
    - Commit transaction and refresh document
    - Call _sync_to_rag_upsert helper
    - Return DocumentResponse
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.6_
  
  - [x] 5.3 Implement get_document method
    - Query document by ID using async select
    - Return DocumentResponse or None if not found
    - _Requirements: 3.1, 3.5_
  
  - [x] 5.4 Implement list_documents method
    - Query total document count
    - Calculate offset from page and page_size
    - Query paginated documents ordered by created_at desc
    - Return list of DocumentResponse and total count
    - _Requirements: 3.3, 3.4, 3.5_
  
  - [x] 5.5 Implement delete_document method
    - Query document by ID
    - Return False if not found
    - Delete document and commit transaction
    - Call _sync_to_rag_delete helper
    - Return True on success
    - _Requirements: 4.1, 4.2, 4.4_
  
  - [x] 5.6 Implement RAG synchronization helpers
    - Implement _sync_to_rag_upsert method with try-except error handling
    - Implement _sync_to_rag_delete method with try-except error handling
    - Log errors without raising exceptions
    - _Requirements: 5.1, 5.2, 5.5, 6.3_

- [x] 6. Checkpoint - Ensure service layer tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implement document router endpoints
  - [x] 7.1 Create document router
    - Create backend/routers/document_router.py
    - Define router with prefix="/documents" and tags=["documents"]
    - Implement get_document_service dependency function
    - _Requirements: 2.1, 3.1, 4.1_
  
  - [x] 7.2 Implement POST /documents endpoint
    - Add upsert_document endpoint accepting DocumentCreate
    - Call service.upsert_document
    - Return DocumentResponse with status 200
    - Handle exceptions and return 500 on error
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [x] 7.3 Implement GET /documents/{document_id} endpoint
    - Add get_document endpoint accepting UUID path parameter
    - Call service.get_document
    - Return DocumentResponse or raise 404 HTTPException
    - _Requirements: 3.1, 3.2, 3.5_
  
  - [x] 7.4 Implement GET /documents endpoint
    - Add list_documents endpoint with page and page_size query parameters
    - Add validation (page >= 1, page_size 1-100)
    - Call service.list_documents
    - Return DocumentListResponse
    - _Requirements: 3.3, 3.4, 3.5_
  
  - [x] 7.5 Implement DELETE /documents/{document_id} endpoint
    - Add delete_document endpoint accepting UUID path parameter
    - Call service.delete_document
    - Return success message or raise 404 HTTPException
    - _Requirements: 4.1, 4.2, 4.3_

- [x] 8. Register document router in main application
  - Import document_router in backend/main.py
  - Add app.include_router(document_router) to register endpoints
  - _Requirements: 2.1, 3.1, 4.1_

- [ ] 9. Write property-based tests for core functionality
  - [ ]* 9.1 Write property test for document creation round-trip
    - **Property 1: Document Creation Round-Trip**
    - **Validates: Requirements 1.2, 2.2, 2.4, 3.1, 3.5**
    - Use hypothesis to generate random text, heading, author
    - Create document, retrieve by ID, verify all fields match
  
  - [ ]* 9.2 Write property test for default status assignment
    - **Property 2: Default Status Assignment**
    - **Validates: Requirements 1.3**
    - Generate documents without status field, verify status="active"
  
  - [ ]* 9.3 Write property test for timestamp management on creation
    - **Property 3: Timestamp Management on Creation**
    - **Validates: Requirements 1.4**
    - Create documents, verify created_at is within 5 seconds of current time
  
  - [ ]* 9.4 Write property test for timestamp update on modification
    - **Property 4: Timestamp Update on Modification**
    - **Validates: Requirements 1.5**
    - Create document, update via upsert, verify updated_at changed and is later
  
  - [ ]* 9.5 Write property test for required field validation
    - **Property 5: Required Field Validation**
    - **Validates: Requirements 2.1, 2.5, 6.1**
    - Generate documents with missing required fields, verify 400 status
  
  - [ ]* 9.6 Write property test for upsert update behavior
    - **Property 6: Upsert Update Behavior**
    - **Validates: Requirements 2.3**
    - Create document, upsert with same ID and different data, verify update
  
  - [ ]* 9.7 Write property test for non-existent document 404
    - **Property 7: Non-Existent Document Returns 404**
    - **Validates: Requirements 3.2, 4.3**
    - Generate random non-existent UUIDs, verify GET and DELETE return 404
  
  - [ ]* 9.8 Write property test for pagination correctness
    - **Property 8: Pagination Correctness**
    - **Validates: Requirements 3.3, 3.4**
    - Create multiple documents, verify pagination returns correct subsets
  
  - [ ]* 9.9 Write property test for delete removes document
    - **Property 9: Delete Removes Document**
    - **Validates: Requirements 4.1, 4.2**
    - Create document, delete it, verify subsequent GET returns 404
  
  - [ ]* 9.10 Write property test for RAG service synchronization
    - **Property 10: RAG Service Synchronization**
    - **Validates: Requirements 2.6, 4.4, 5.1, 5.2**
    - Mock RAG client, perform upsert/delete, verify RAG methods called with correct data
  
  - [ ]* 9.11 Write property test for RAG service failure resilience
    - **Property 11: RAG Service Failure Resilience**
    - **Validates: Requirements 5.5, 6.3**
    - Mock RAG client to raise exceptions, verify CRUD operations still succeed
  
  - [ ]* 9.12 Write property test for UUID validation
    - **Property 12: UUID Validation**
    - **Validates: Requirements 6.5**
    - Generate invalid UUID strings, verify appropriate error responses
  
  - [ ]* 9.13 Write property test for database session lifecycle
    - **Property 13: Database Session Lifecycle**
    - **Validates: Requirements 8.5**
    - Verify database sessions are closed even when operations fail

- [ ] 10. Write unit tests for edge cases and error conditions
  - [ ]* 10.1 Write unit tests for document model
    - Test model instantiation with all fields
    - Test default values (status="active")
    - Test timestamp auto-generation
    - _Requirements: 1.2, 1.3, 1.4, 1.5_
  
  - [ ]* 10.2 Write unit tests for document service edge cases
    - Test empty database list
    - Test single document in database
    - Test maximum length strings
    - Test very large text content
    - Test page beyond available results
    - _Requirements: 3.3, 3.4_
  
  - [ ]* 10.3 Write unit tests for RAG client implementations
    - Test HTTPRAGClient upsert and delete methods
    - Test timeout handling
    - Test error response handling
    - Mock httpx AsyncClient for testing
    - _Requirements: 5.1, 5.2, 5.4_
  
  - [ ]* 10.4 Write unit tests for error handling
    - Test missing required fields returns 400
    - Test invalid UUID format returns 400/422
    - Test non-existent document returns 404
    - Mock database failures to test 500 responses
    - _Requirements: 2.5, 3.2, 4.3, 6.1, 6.2, 6.4, 6.5_
  
  - [ ]* 10.5 Write integration tests for configuration
    - Test configuration loading from environment variables
    - Test default values when env vars not set
    - Test HTTP vs gRPC protocol selection
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 11. Create test fixtures and configuration
  - [ ]* 11.1 Create pytest configuration
    - Create backend/test/conftest.py with shared fixtures
    - Add async test database fixture
    - Add test client fixture for FastAPI
    - Add mock RAG client fixture
    - Configure pytest-asyncio
  
  - [ ]* 11.2 Set up test database
    - Add test database configuration
    - Add fixture to create/drop test tables
    - Add fixture to clean database between tests

- [-] 12. Final checkpoint - Run all tests and verify coverage
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties with 100+ iterations
- Unit tests validate specific examples, edge cases, and error conditions
- RAG service integration is designed to be non-blocking (failures don't fail CRUD operations)
- The implementation follows existing codebase patterns (SQLAlchemy async, FastAPI, environment config)
