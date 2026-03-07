"""
Unit tests for Policy Retrieval Node
Tests the policy retrieval functionality in the LangGraph workflow
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.ai_nodes.policy_retrieval_node import policy_retrieval_node
from services.ai_nodes.graph_state import GraphState
from schemas.rag_schema import RAGSearchResponse, RAGRelevantPart


@pytest.mark.asyncio
async def test_policy_retrieval_node_success():
    """Verify policy_retrieval_node successfully retrieves policies"""
    # Mock state
    state: GraphState = {
        "problem_statement": "Water supply issue in residential area",
        "retrieved_policies": [],
        "selected_activity_ids": [],
        "selected_activities": [],
        "workflow_json": {},
        "validation_result": {},
        "error": "",
        "current_step": "",
        "message": ""
    }
    
    # Mock RAG response
    mock_rag_response = RAGSearchResponse(
        relevant_parts=[
            RAGRelevantPart(
                document_id="doc-123",
                text="Water supply regulations require...",
                heading="Water Supply Policy",
                author="Water Department",
                chunk_index=1.0,
                original_id="doc-123",
                is_chunk=False,
                similarity_score=0.95,
                status="active",
                source="hybrid",
                semantic_score=0.9,
                lexical_score=0.85,
                combined_score=0.9
            )
        ],
        total_results=1
    )
    
    # Mock RAG client
    mock_rag_client = AsyncMock()
    mock_rag_client.search_documents = AsyncMock(return_value=mock_rag_response)
    
    with patch("services.ai_nodes.policy_retrieval_node.get_rag_client", return_value=mock_rag_client):
        result = await policy_retrieval_node(state)
    
    # Verify results
    assert result["current_step"] == "policy_retrieval_complete"
    assert len(result["retrieved_policies"]) == 1
    assert result["retrieved_policies"][0]["heading"] == "Water Supply Policy"
    assert result["retrieved_policies"][0]["similarity_score"] == 0.95
    assert result["error"] == ""
    assert "Retrieved 1 relevant policies" in result["message"]


@pytest.mark.asyncio
async def test_policy_retrieval_node_empty_results():
    """Verify policy_retrieval_node handles empty results"""
    state: GraphState = {
        "problem_statement": "Unknown issue",
        "retrieved_policies": [],
        "selected_activity_ids": [],
        "selected_activities": [],
        "workflow_json": {},
        "validation_result": {},
        "error": "",
        "current_step": "",
        "message": ""
    }
    
    # Mock empty RAG response
    mock_rag_response = RAGSearchResponse(
        relevant_parts=[],
        total_results=0
    )
    
    mock_rag_client = AsyncMock()
    mock_rag_client.search_documents = AsyncMock(return_value=mock_rag_response)
    
    with patch("services.ai_nodes.policy_retrieval_node.get_rag_client", return_value=mock_rag_client):
        result = await policy_retrieval_node(state)
    
    assert result["current_step"] == "policy_retrieval_complete"
    assert len(result["retrieved_policies"]) == 0
    assert result["error"] == ""


@pytest.mark.asyncio
async def test_policy_retrieval_node_error_handling():
    """Verify policy_retrieval_node handles errors gracefully"""
    state: GraphState = {
        "problem_statement": "Test problem",
        "retrieved_policies": [],
        "selected_activity_ids": [],
        "selected_activities": [],
        "workflow_json": {},
        "validation_result": {},
        "error": "",
        "current_step": "",
        "message": ""
    }
    
    # Mock RAG client that raises an exception
    mock_rag_client = AsyncMock()
    mock_rag_client.search_documents = AsyncMock(side_effect=Exception("RAG service unavailable"))
    
    with patch("services.ai_nodes.policy_retrieval_node.get_rag_client", return_value=mock_rag_client):
        result = await policy_retrieval_node(state)
    
    assert result["error"] == "Policy retrieval failed: RAG service unavailable"
    assert result["retrieved_policies"] == []


@pytest.mark.asyncio
async def test_policy_retrieval_node_skips_on_previous_error():
    """Verify policy_retrieval_node skips execution if previous node had error"""
    state: GraphState = {
        "problem_statement": "Test problem",
        "retrieved_policies": [],
        "selected_activity_ids": [],
        "selected_activities": [],
        "workflow_json": {},
        "validation_result": {},
        "error": "Previous node error",
        "current_step": "",
        "message": ""
    }
    
    result = await policy_retrieval_node(state)
    
    # Should return state unchanged
    assert result["error"] == "Previous node error"
    assert result["retrieved_policies"] == []


@pytest.mark.asyncio
async def test_policy_retrieval_node_uses_config_namespace():
    """Verify policy_retrieval_node uses configured namespace"""
    state: GraphState = {
        "problem_statement": "Test problem",
        "retrieved_policies": [],
        "selected_activity_ids": [],
        "selected_activities": [],
        "workflow_json": {},
        "validation_result": {},
        "error": "",
        "current_step": "",
        "message": ""
    }
    
    mock_rag_response = RAGSearchResponse(relevant_parts=[], total_results=0)
    mock_rag_client = AsyncMock()
    mock_rag_client.search_documents = AsyncMock(return_value=mock_rag_response)
    
    with patch("services.ai_nodes.policy_retrieval_node.get_rag_client", return_value=mock_rag_client):
        with patch("services.ai_nodes.policy_retrieval_node.settings") as mock_settings:
            mock_settings.RAG_NAMESPACE = "test-namespace"
            await policy_retrieval_node(state)
    
    # Verify the search request used the configured namespace
    call_args = mock_rag_client.search_documents.call_args
    search_request = call_args[0][0]
    assert search_request.namespace == "test-namespace"
