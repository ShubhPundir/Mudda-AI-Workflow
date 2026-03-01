# Policy Retrieval Integration

## Overview
This document describes the integration of the Policy Retrieval node into the LangGraph workflow for the Mudda AI Workflow System.

## Architecture

### New LangGraph Workflow Structure
```
START → policy_retrieval → activity_selector → plan_maker → plan_validator → END
```

The workflow now includes a new first step that retrieves relevant policies from the knowledge base before selecting activities and creating workflow plans.

## Components Added

### 1. Policy Retrieval Node
**File:** `backend/services/ai_nodes/policy_retrieval_node.py`

**Purpose:** Retrieves relevant policies from the internal knowledge base using RAG (Retrieval-Augmented Generation).

**Key Features:**
- Uses the RAG client to search for relevant policy documents
- Configurable search parameters (top_k=5, similarity_threshold=0.6)
- Formats retrieved policies for downstream nodes
- Handles errors gracefully
- Logs retrieval operations for debugging

**Input:** 
- `problem_statement` from GraphState

**Output:**
- `retrieved_policies` - List of relevant policy documents with metadata

### 2. Updated Graph State
**File:** `backend/services/ai_nodes/graph_state.py`

**Changes:**
- Added `retrieved_policies: List[Dict[str, Any]]` field to track policies retrieved from RAG

### 3. Enhanced Activity Selector Node
**File:** `backend/services/ai_nodes/activity_selector_node.py`

**Changes:**
- Now receives `retrieved_policies` from previous node
- Incorporates policy context into activity selection prompt
- Selects activities that comply with applicable regulations
- Updated agent number from "Agent 1" to "Agent 2"

### 4. Enhanced Plan Maker Node
**File:** `backend/services/ai_nodes/plan_maker_node.py`

**Changes:**
- Now receives `retrieved_policies` from state
- Incorporates policy context into workflow generation prompt
- Ensures workflow plans comply with regulations
- Updated agent number from "Agent 2" to "Agent 3"

### 5. New Policy Retrieval Prompt
**File:** `backend/services/ai_nodes/prompts.py`

**Added:** `get_policy_retrieval_prompt()` function

**Purpose:** Provides system prompt for policy retrieval context and strategy.

### 6. Updated AI Service
**File:** `backend/services/ai_service.py`

**Changes:**
- Added `policy_retrieval` node to the workflow graph
- Updated graph edges to include policy retrieval as first step
- Added `retrieved_policies` to initial state
- Added streaming support for policy retrieval events
- Updated agent name mapping

### 7. Configuration Updates
**File:** `backend/config.py`

**Added:**
- `RAG_NAMESPACE` configuration setting (default: "waterworks-department")

**Files:** `backend/.env` and `backend/example/env_example`

**Added:**
- `RAG_NAMESPACE=waterworks-department` environment variable

### 8. Tests
**File:** `backend/test/test_policy_retrieval_node.py`

**Test Coverage:**
- Successful policy retrieval
- Empty results handling
- Error handling
- Skip on previous error
- Configuration namespace usage

## How It Works

### 1. Policy Retrieval Flow
```python
# User submits problem statement
problem_statement = "Water supply issue in residential area"

# Policy Retrieval Node
1. Receives problem statement
2. Creates RAG search request with:
   - query: problem_statement
   - top_k: 5 (retrieve top 5 most relevant documents)
   - similarity_threshold: 0.6 (minimum relevance)
   - namespace: configured namespace (e.g., "waterworks-department")
3. Executes search via RAG client
4. Formats results into policy objects
5. Updates state with retrieved_policies

# Activity Selector Node
1. Receives problem statement + retrieved policies
2. Analyzes policies to understand regulatory requirements
3. Selects activities that comply with policies
4. Updates state with selected activities

# Plan Maker Node
1. Receives selected activities + retrieved policies
2. Creates workflow plan that complies with policies
3. Updates state with workflow_json

# Plan Validator Node
1. Validates the workflow plan
2. Returns final validated workflow
```

### 2. Policy Data Structure
```python
{
    "document_id": "doc-123",
    "heading": "Water Supply Policy",
    "author": "Water Department",
    "text": "Full policy text content...",
    "similarity_score": 0.95,
    "source": "hybrid"  # hybrid, semantic, or lexical
}
```

### 3. RAG Search Request
```python
RAGSearchRequest(
    query="Water supply issue in residential area",
    top_k=5,
    similarity_threshold=0.6,
    namespace="waterworks-department"
)
```

## Configuration

### Environment Variables
```bash
# RAG Service Configuration
RAG_SERVICE_URL=http://localhost:8082
RAG_PROTOCOL=http
RAG_GRPC_ADDRESS=localhost:8082
RAG_NAMESPACE=waterworks-department
```

### Customization Options

**Adjust Search Parameters:**
Edit `backend/services/ai_nodes/policy_retrieval_node.py`:
```python
search_request = RAGSearchRequest(
    query=problem_statement,
    top_k=10,  # Increase to retrieve more policies
    similarity_threshold=0.7,  # Increase for stricter relevance
    namespace=settings.RAG_NAMESPACE
)
```

**Change Namespace:**
Update `.env` file:
```bash
RAG_NAMESPACE=your-custom-namespace
```

## Benefits

1. **Policy-Aware Workflows:** Workflows are now generated with awareness of relevant policies and regulations
2. **Compliance:** Ensures workflow plans comply with applicable regulations
3. **Context-Rich Planning:** Activity selection and workflow generation are informed by official policy documents
4. **Flexible Configuration:** Easy to adjust search parameters and namespace
5. **Error Resilient:** Gracefully handles RAG service failures
6. **Testable:** Comprehensive test coverage for policy retrieval functionality

## Streaming Events

The policy retrieval node emits the following streaming events:

### policy_retrieval_start
```json
{
    "event": "policy_retrieval_start",
    "data": {
        "message": "Agent 1: Retrieving relevant policies from knowledge base...",
        "agent": "policy_retrieval"
    }
}
```

### policy_retrieval_complete
```json
{
    "event": "policy_retrieval_complete",
    "data": {
        "message": "Agent 1: Retrieved 3 relevant policies from knowledge base",
        "agent": "policy_retrieval",
        "policies": [
            {
                "heading": "Water Supply Policy",
                "author": "Water Department",
                "similarity_score": 0.95
            }
        ]
    }
}
```

## Future Enhancements

1. **Policy Caching:** Cache frequently accessed policies to reduce RAG queries
2. **Policy Ranking:** Implement more sophisticated policy ranking algorithms
3. **Multi-Namespace Search:** Support searching across multiple namespaces
4. **Policy Summarization:** Use LLM to summarize long policy documents
5. **Policy Versioning:** Track and use specific versions of policies
6. **Feedback Loop:** Learn from workflow execution to improve policy retrieval

## Troubleshooting

### No Policies Retrieved
- Check RAG service is running and accessible
- Verify `RAG_SERVICE_URL` is correct
- Check `RAG_NAMESPACE` matches your document namespace
- Lower `similarity_threshold` to retrieve more results

### RAG Service Errors
- Check RAG service logs
- Verify network connectivity
- Ensure documents are indexed in the RAG service
- Check authentication/authorization if applicable

### Incorrect Policies Retrieved
- Review and improve problem statement clarity
- Adjust `similarity_threshold` for stricter matching
- Verify document indexing in RAG service
- Consider re-indexing documents with better metadata
