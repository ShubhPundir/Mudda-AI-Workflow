"""
Policy Retrieval Node for LangGraph workflow
Retrieves relevant policies from the internal knowledge base using RAG
"""
import logging
from typing import Dict, Any
from config import settings
from infrastructure.rag import get_rag_client
from schemas.rag_schema import RAGSearchRequest
from .graph_state import GraphState
from .prompts import get_policy_retrieval_prompt

logger = logging.getLogger(__name__)


async def policy_retrieval_node(state: GraphState) -> GraphState:
    """
    Node for retrieving relevant policies from the knowledge base
    
    This node:
    1. Takes the problem statement from the state
    2. Uses RAG to search for relevant policies in the knowledge base
    3. Formats the retrieved policies for use in workflow planning
    4. Gracefully skips if RAG service is unavailable
    5. Returns updated state with retrieved_policies (empty if unavailable)
    
    Args:
        state: Current graph state containing problem_statement
        
    Returns:
        Updated graph state with retrieved_policies
    """
    # Early return if there's an error from previous node
    if state.get("error"):
        return state

    problem_statement = state["problem_statement"]
    
    new_state = state.copy()
    new_state["current_step"] = "policy_retrieval_start"
    new_state["message"] = "Agent 1: Retrieving relevant policies from knowledge base..."

    try:
        # Get RAG client
        rag_client = get_rag_client()
        
        # Check if RAG client is available
        if rag_client is None:
            logger.warning("RAG service is not available, skipping policy retrieval")
            new_state["retrieved_policies"] = []
            new_state["current_step"] = "policy_retrieval_complete"
            new_state["message"] = "Agent 1: RAG service unavailable - proceeding without policy context"
            return new_state
        
        # Create search request with optimized parameters for policy retrieval
        search_request = RAGSearchRequest(
            query=problem_statement,
            top_k=5,  # Retrieve top 5 most relevant policy documents
            similarity_threshold=0.6,  # Minimum relevance threshold
            namespace=settings.RAG_NAMESPACE  # Use configured namespace
        )
        
        # Execute search
        logger.info(f"Searching for policies related to: {problem_statement[:100]}...")
        search_response = await rag_client.search_documents(search_request)
        
        # Format retrieved policies for downstream nodes
        retrieved_policies = []
        for part in search_response.relevant_parts:
            policy_info = {
                "document_id": part.document_id,
                "heading": part.heading,
                "author": part.author,
                "text": part.text,
                "similarity_score": part.similarity_score,
                "source": part.source
            }
            retrieved_policies.append(policy_info)
        
        logger.info(f"Retrieved {len(retrieved_policies)} relevant policy documents")
        
        # Update state with retrieved policies
        new_state["retrieved_policies"] = retrieved_policies
        new_state["current_step"] = "policy_retrieval_complete"
        
        if len(retrieved_policies) > 0:
            new_state["message"] = f"Agent 1: Retrieved {len(retrieved_policies)} relevant policies from knowledge base"
        else:
            new_state["message"] = "Agent 1: No relevant policies found - proceeding with general workflow generation"
        
        return new_state
        
    except Exception as e:
        # Log the error but don't fail the entire workflow
        logger.warning(f"Policy retrieval failed, continuing without policies: {str(e)}")
        
        # Continue with empty policies instead of failing
        new_state["retrieved_policies"] = []
        new_state["current_step"] = "policy_retrieval_complete"
        new_state["message"] = f"Agent 1: Policy retrieval unavailable ({str(e)[:50]}...) - proceeding without policy context"
        
        return new_state
