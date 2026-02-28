"""
Activity Selector Node for LangGraph workflow
Analyzes problem statements and selects relevant activities
"""
import json
from typing import Dict, Any
from activities.registry import ACTIVITY_METADATA
from sessions.llm.llm_factory import LLMFactory
from schemas.ai_schemas import ActivitySelectionResponse
from .graph_state import GraphState
from .prompts import get_activity_selection_prompt


async def activity_selector_node(state: GraphState) -> GraphState:
    """
    Node for selecting relevant activities using structured output
    
    This node:
    1. Analyzes the problem statement
    2. Reviews available activities from the registry
    3. Uses LLM with structured output to select relevant activities
    4. Returns updated state with selected activities
    
    Args:
        state: Current graph state containing problem_statement
        
    Returns:
        Updated graph state with selected_activity_ids and selected_activities
    """
    problem_statement = state["problem_statement"]
    
    # Update progress
    new_state = state.copy()
    new_state["current_step"] = "activity_selection_start"
    new_state["message"] = "Agent 1: Analyzing problem and selecting activities..."

    try:
        # Get LLM service
        llm = LLMFactory.get_llm_service()
        
        # Use static metadata from registry
        activities_list = list(ACTIVITY_METADATA.values())
        
        # Build prompt
        system_prompt = get_activity_selection_prompt()
        selection_prompt = f"""
Problem Statement: {problem_statement}

Available Activities:
{json.dumps(activities_list, indent=2)}

Select the activity IDs that are relevant for solving this problem.
"""
        
        prompt = f"{system_prompt}\n\n{selection_prompt}"
        
        # Use structured output - no regex needed!
        selection_result = await llm.generate_structured(
            prompt, 
            ActivitySelectionResponse
        )
        
        selected_ids = selection_result.selected_activity_ids
        if not selected_ids:
            raise ValueError("No activities were selected")

        # Get full details for selected activities
        selected_activities = [
            ACTIVITY_METADATA[aid] 
            for aid in selected_ids 
            if aid in ACTIVITY_METADATA
        ]

        new_state["selected_activity_ids"] = selected_ids
        new_state["selected_activities"] = selected_activities
        new_state["current_step"] = "activity_selection_complete"
        new_state["message"] = f"Agent 1: Selected {len(selected_ids)} activities"
        return new_state
        
    except Exception as e:
        new_state["error"] = str(e)
        return new_state
