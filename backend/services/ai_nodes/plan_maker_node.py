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
    1. Takes selected activities and retrieved policies from previous nodes
    2. Uses LLM with structured output to generate a workflow plan
    3. Validates the plan (DAG structure, activity IDs)
    4. Returns updated state with workflow_json
    
    Args:
        state: Current graph state containing selected_activities and retrieved_policies
        
    Returns:
        Updated graph state with workflow_json
    """
    # Early return if there's an error from previous node
    if state.get("error"):
        return state

    problem_statement = state["problem_statement"]
    activities_dict = state["selected_activities"]
    retrieved_policies = state.get("retrieved_policies", [])
    
    new_state = state.copy()
    new_state["current_step"] = "workflow_generation_start"
    new_state["message"] = "Agent 3: Creating workflow plan based on policies and activities..."

    try:
        # Get LLM service
        llm = LLMFactory.get_llm_service()
        
        # Format retrieved policies for the prompt
        policies_context = ""
        if retrieved_policies:
            policies_context = "\n\nRelevant Policies and Regulations:\n"
            for idx, policy in enumerate(retrieved_policies, 1):
                policies_context += f"\n{idx}. {policy['heading']} (by {policy['author']})\n"
                policies_context += f"   Content: {policy['text'][:500]}...\n"
            policies_context += "\nEnsure the workflow plan complies with these policies and regulations.\n"
        
        # Build prompt
        system_prompt = get_workflow_generation_prompt()
        workflow_prompt = f"""
Problem Statement: {problem_statement}
{policies_context}

Selected Activities:
{json.dumps(activities_dict, indent=2)}

Generate a workflow plan to resolve this problem using the selected activities.
The workflow must comply with the relevant policies and regulations provided above.
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
        new_state["message"] = "Agent 3: Workflow plan created successfully with policy compliance"
        return new_state
        
    except Exception as e:
        new_state["error"] = str(e)
        return new_state
