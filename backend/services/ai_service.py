"""
AI Service for workflow generation using Gemini AI and LangGraph orchestration
Uses structured output with Pydantic validation - zero regex extraction
"""
import json
import asyncio
from typing import Dict, Any, List, TypedDict
from activities.registry import ACTIVITY_METADATA
# LangGraph imports
from langgraph.graph import StateGraph, END
from sessions.llm.llm_factory import LLMFactory
# Structured output schemas
from schemas.ai_schemas import (
    ActivitySelectionResponse,
    WorkflowPlanResponse,
    WorkflowStep
)

class GraphState(TypedDict):
    """State management for LangGraph"""
    problem_statement: str
    selected_activity_ids: List[str]
    selected_activities: List[Dict[str, Any]]
    workflow_json: Dict[str, Any]
    error: str
    # Progress tracking for streaming
    current_step: str
    message: str


class AIService:
    """
    AI Service for generating workflow plans using Gemini AI and LangGraph
    """

    def __init__(self):
        self.llm = LLMFactory.get_llm_service()
        self._setup_graph()

    def _setup_graph(self):
        """Initialize the LangGraph state machine"""
        workflow = StateGraph(GraphState)

        # Define nodes
        workflow.add_node("activity_selector", self._activity_selector_node)
        workflow.add_node("plan_maker", self._plan_maker_node)

        # Define edges
        workflow.set_entry_point("activity_selector")
        workflow.add_edge("activity_selector", "plan_maker")
        workflow.add_edge("plan_maker", END)

        self.app = workflow.compile()

    async def _activity_selector_node(self, state: GraphState) -> GraphState:
        """Node for selecting relevant activities using structured output"""
        problem_statement = state["problem_statement"]
        
        # Update progress
        new_state = state.copy()
        new_state["current_step"] = "activity_selection_start"
        new_state["message"] = "Agent 1: Analyzing problem and selecting activities..."

        try:
            # Use static metadata from registry
            activities_list = list(ACTIVITY_METADATA.values())
            
            system_prompt = self._get_activity_selection_prompt()
            selection_prompt = f"""
Problem Statement: {problem_statement}

Available Activities:
{json.dumps(activities_list, indent=2)}

Select the activity IDs that are relevant for solving this problem.
"""
            
            prompt = f"{system_prompt}\n\n{selection_prompt}"
            
            # Use structured output - no regex needed!
            selection_result = await self.llm.generate_structured(
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

    async def _plan_maker_node(self, state: GraphState) -> GraphState:
        """Node for creating the workflow plan using structured output"""
        if state.get("error"):
            return state

        problem_statement = state["problem_statement"]
        activities_dict = state["selected_activities"]
        
        new_state = state.copy()
        new_state["current_step"] = "workflow_generation_start"
        new_state["message"] = "Agent 2: Creating workflow plan..."

        try:
            system_prompt = self._get_workflow_generation_prompt()
            workflow_prompt = f"""
Problem Statement: {problem_statement}

Selected Activities:
{json.dumps(activities_dict, indent=2)}

Generate a workflow plan to resolve this problem using the selected activities.
"""
            
            prompt = f"{system_prompt}\n\n{workflow_prompt}"
            
            # Use structured output - no regex needed!
            workflow_plan = await self.llm.generate_structured(
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

    @staticmethod
    def _get_activity_selection_prompt() -> str:
        """Get the system prompt for activity selection"""
        return """
You are "Mudda AI Activity Selector", an expert at identifying atomic activities for civic issue resolution.

### CONTEXT
Workflows are composed of **Temporal activities only**. Each activity represents a single logical operation.

### TASK
Given a problem statement, analyze the available activities and select ONLY the ones relevant for solving the issue.

### OUTPUT FORMAT
You MUST respond with a JSON object matching this exact structure:
{
  "selected_activity_ids": ["activity-id-1", "activity-id-2"]
}

### RULES:
1. Select only activities that are directly relevant to solving the problem
2. Be selective - don't include unnecessary steps
3. You must select at least one activity
4. Return ONLY the JSON object, no additional text or markdown
"""

    @staticmethod
    def _get_workflow_generation_prompt() -> str:
        """Get the system prompt for workflow generation"""
        return """
You are "Mudda AI Workflow Planner", an expert in government service orchestration using Temporal.io.

### CONTEXT
All workflows are composed of **Temporal activities only**. Each activity represents a single logical operation.

### TASK
Using the provided activities, **design an actionable end-to-end plan** to resolve the problem.
The plan must follow a **directed acyclic graph (DAG)** structure, where each step references one activity by `id`.

### OUTPUT FORMAT
You MUST respond with a JSON object matching this exact structure:
{
  "workflow_name": "<short_name>",
  "description": "<workflow_description>",
  "steps": [
    {
      "step_id": "<step_identifier>",
      "activity_id": "<activity_id>",
      "description": "<description_of_step>",
      "inputs": { "<input_name>": "<value_or_template>" },
      "outputs": ["<output_name>"],
      "next": ["<next_step_id>"]
    }
  ]
}

### RULES:
1. Use only the provided activities - do not create fictional ones
2. Every step MUST have an `activity_id` that exists in the provided activities
3. Use template variables like {{input_name}} or {{step_id.output_key}} for dynamic inputs
4. Return ONLY the JSON object, no additional text or markdown
5. The workflow must be a valid DAG — no cycles allowed
6. All step_ids must be unique
7. All referenced next step_ids must exist in the workflow
"""



    async def generate_workflow_plan(self, problem_statement: str) -> Dict[str, Any]:
        """Generate a workflow plan using LangGraph"""
        initial_state = {
            "problem_statement": problem_statement,
            "selected_activity_ids": [],
            "selected_activities": [],
            "workflow_json": {},
            "error": "",
            "current_step": "",
            "message": ""
        }
        
        final_state = await self.app.ainvoke(initial_state)
        
        if final_state.get("error"):
            raise ValueError(final_state["error"])
            
        return final_state["workflow_json"]

    async def generate_workflow_plan_stream(self, problem_statement: str):
        """Generate a workflow plan with streaming updates using LangGraph"""
        initial_state = {
            "problem_statement": problem_statement,
            "selected_activity_ids": [],
            "selected_activities": [],
            "workflow_json": {},
            "error": "",
            "current_step": "",
            "message": ""
        }
        
        try:
            # Use astream to get updates from each node
            async for output in self.app.astream(initial_state):
                for node_name, state in output.items():
                    if state.get("error"):
                        yield {
                            "event": "error",
                            "data": {"message": state["error"], "error": True}
                        }
                        return

                    event_type = state.get("current_step")
                    if not event_type:
                        continue
                        
                    data = {
                        "message": state.get("message", ""),
                        "agent": "activity_selector" if node_name == "activity_selector" else "plan_maker"
                    }
                    
                    if event_type == "activity_selection_complete":
                        data["activities"] = [
                            {"id": a["id"], "name": a["name"], "description": a["description"]}
                            for a in state.get("selected_activities", [])
                        ]
                    elif event_type == "workflow_generation_complete":
                        data["workflow"] = state.get("workflow_json")
                        
                    yield {
                        "event": event_type,
                        "data": data
                    }
        except Exception as e:
            yield {
                "event": "error",
                "data": {"message": str(e), "error": True}
            }


# Global AI service instance
ai_service = AIService()
