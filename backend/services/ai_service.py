"""
AI Service for workflow generation using Gemini AI and LangGraph orchestration
"""
import json
import re
import asyncio
from typing import Dict, Any, List, TypedDict, Annotated, Union
from activities.registry import ACTIVITY_METADATA
# LangGraph imports
from langgraph.graph import StateGraph, END
from sessions.llm.llm_factory import LLMFactory

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
        """Node for selecting relevant activities"""
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
            response = await self.llm.generate_async(prompt)
            
            response_text = self._serialize_ai_response(response.text if hasattr(response, "text") else str(response))
            selection_result = json.loads(response_text)
            
            selected_ids = selection_result.get("selected_activity_ids", [])
            if not selected_ids:
                raise ValueError("No activities were selected")

            # Get full details for selected activities
            selected_activities = [ACTIVITY_METADATA[aid] for aid in selected_ids if aid in ACTIVITY_METADATA]

            new_state["selected_activity_ids"] = selected_ids
            new_state["selected_activities"] = selected_activities
            new_state["current_step"] = "activity_selection_complete"
            new_state["message"] = f"Agent 1: Selected {len(selected_ids)} activities"
            return new_state
        except Exception as e:
            new_state["error"] = str(e)
            return new_state

    async def _plan_maker_node(self, state: GraphState) -> GraphState:
        """Node for creating the workflow plan"""
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
            response = await self.llm.generate_async(prompt)
            
            response_text = self._serialize_ai_response(response.text if hasattr(response, "text") else str(response))
            workflow_json = json.loads(response_text)
            
            # Validate
            self._validate_workflow(workflow_json, activities_dict)
            
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
Respond ONLY in **valid JSON** matching this schema:

```json
{
  "selected_activity_ids": ["activity-id-1", "activity-id-2"]
}
```

### RULES:
1. Select only activities that are directly relevant to solving the problem
2. Be selective - don't include unnecessary steps
3. Return ONLY valid JSON
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
Respond ONLY in **valid JSON** matching this schema:

```json
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
```

### RULES:
1. Use only the provided activities - do not create fictional ones
2. Every step MUST have an `activity_id`.
3. Use template variables like {{input_name}} or {{step_id.output_key}} for dynamic inputs.
4. Return ONLY valid JSON, no additional text.
5. The workflow must be valid DAG — no cycles.
"""

    @staticmethod
    def _serialize_ai_response(response_text: str) -> str:
        """Extract and serialize JSON from AI response"""
        if not response_text:
            raise ValueError("Empty response from AI model")
        
        response_text = response_text.strip()
        
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            return json_match.group(1)
        
        # Try to find JSON object in the text
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        return response_text

    @staticmethod
    def _validate_workflow(workflow: Dict[str, Any], activities: List[dict]) -> None:
        """Validate the generated workflow structure"""
        required_fields = ["workflow_name", "description", "steps"]
        
        for field in required_fields:
            if field not in workflow:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(workflow["steps"], list):
            raise ValueError("Steps must be a list")
        
        activity_ids = {act["id"] for act in activities}
        
        for i, step in enumerate(workflow["steps"]):
            if "step_id" not in step:
                raise ValueError(f"Step {i} missing step_id")
            if "activity_id" not in step:
                raise ValueError(f"Step {i} missing activity_id")
            if step["activity_id"] not in activity_ids:
                raise ValueError(f"Step {i} references non-existent activity: {step['activity_id']}")

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
