"""
Graph state definition for LangGraph workflow orchestration
"""
from typing import Dict, Any, List, TypedDict


class GraphState(TypedDict):
    """
    State management for LangGraph workflow execution
    
    This state is passed between nodes and tracks the entire workflow execution.
    """
    problem_statement: str
    selected_activity_ids: List[str]
    selected_activities: List[Dict[str, Any]]
    workflow_json: Dict[str, Any]
    error: str
    # Progress tracking for streaming
    current_step: str
    message: str
