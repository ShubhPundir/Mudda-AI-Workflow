"""
Plan Maker Node for LangGraph workflow
Creates detailed workflow plans from selected activities
"""
import json
from typing import Dict, Any
from sessions.llm.llm_factory import LLMFactory
from schemas.ai_schemas import WorkflowPlanResponse
from .graph_state import GraphState
from .prompts import get_workflow_generation_prompt


async def plan_maker_node(state: GraphState) -> GraphState:
    """
    Node for creating the workflow plan using structured output
    
    This node:
    1. Takes selected activities from previous node
    2. Uses LLM with structured output to generate a workflow plan
    3. Validates the plan (DAG structure, activity IDs)
    4. Returns updated state with workflow_json
    
    Args:
        state: Current graph state containing selected_activities
        
    Returns:
        Updated graph state with workflow_json
    """
    # Early return if there's an error from previous node
    if state.get("error"):
        return state

    problem_statement = state["problem_statement"]
    activities_dict = state["selected_activities"]
    
    new_state = state.copy()
    new_state["current_step"] = "workflow_generation_start"
    new_state["message"] = "Agent 2: Creating workflow plan..."

    try:
        # Get LLM service
        llm = LLMFactory.get_llm_service()
        
        # Build prompt
        system_prompt = get_workflow_generation_prompt()
        workflow_prompt = f"""
Problem Statement: {problem_statement}

Selected Activities:
{json.dumps(activities_dict, indent=2)}

Generate a workflow plan to resolve this problem using the selected activities.
"""
        
        prompt = f"{system_prompt}\n\n{workflow_prompt}"
        
        # Use structured output - no regex needed!
        workflow_plan = await llm.generate_structured(
            prompt,
            WorkflowPlanResponse
        )
        
        # Additional validation: check activity IDs exist
        activity_ids = {act["id"] for act in activities_dict}
        workflow_plan.validate_activity_ids(activity_ids)
        
        # Convert to dict for state storage
        workflow_json = workflow_plan.model_dump()
        
        new_state["workflow_json"] = workflow_json
        new_state["current_step"] = "workflow_generation_complete"
        new_state["message"] = "Agent 2: Workflow plan created successfully"
        return new_state
        
    except Exception as e:
        new_state["error"] = str(e)
        return new_state
