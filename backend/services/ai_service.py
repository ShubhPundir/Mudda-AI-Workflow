"""
AI Service for workflow generation using Gemini AI and LangGraph orchestration
"""
import json
import re
import asyncio
from typing import Dict, Any, List, TypedDict, Annotated, Union
from sqlalchemy.ext.asyncio import AsyncSession
from services.component_service import ComponentService
# LangGraph imports
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from sessions.llm.llm_factory import LLMFactory

class GraphState(TypedDict):
    """State management for LangGraph"""
    db: AsyncSession
    problem_statement: str
    selected_component_ids: List[str]
    selected_components: List[Dict[str, Any]]
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
        workflow.add_node("component_selector", self._component_selector_node)
        workflow.add_node("plan_maker", self._plan_maker_node)

        # Define edges
        workflow.set_entry_point("component_selector")
        workflow.add_edge("component_selector", "plan_maker")
        workflow.add_edge("plan_maker", END)

        self.app = workflow.compile()

    async def _component_selector_node(self, state: GraphState) -> GraphState:
        """Node for selecting relevant components"""
        db = state["db"]
        problem_statement = state["problem_statement"]
        
        # Update progress
        new_state = state.copy()
        new_state["current_step"] = "component_selection_start"
        new_state["message"] = "Agent 1: Analyzing problem and selecting components..."

        try:
            # Get minimal component info
            components = await ComponentService.get_components_for_selection(db)
            if not components:
                raise ValueError("No active components available in the system")
            
            components_dict = [component.model_dump() for component in components]
            
            system_prompt = self._get_component_selection_prompt()
            selection_prompt = f"""
Problem Statement: {problem_statement}

Available Components (minimal info):
{json.dumps(components_dict, indent=2)}

Select the component IDs that are relevant for solving this problem.
"""
            
            prompt = f"{system_prompt}\n\n{selection_prompt}"
            response = await self.llm.generate_async(prompt)
            
            response_text = self._serialize_ai_response(response.text if hasattr(response, "text") else str(response))
            selection_result = json.loads(response_text)
            
            selected_ids = selection_result.get("selected_component_ids", [])
            if not selected_ids:
                raise ValueError("No components were selected")

            # Get full details for selected components
            selected_components_objs = await ComponentService.get_components_by_ids(db, selected_ids)
            selected_components = [comp.model_dump() for comp in selected_components_objs]

            new_state["selected_component_ids"] = selected_ids
            new_state["selected_components"] = selected_components
            new_state["current_step"] = "component_selection_complete"
            new_state["message"] = f"Agent 1: Selected {len(selected_ids)} components"
            return new_state
        except Exception as e:
            new_state["error"] = str(e)
            return new_state

    async def _plan_maker_node(self, state: GraphState) -> GraphState:
        """Node for creating the workflow plan"""
        if state.get("error"):
            return state

        problem_statement = state["problem_statement"]
        components_dict = state["selected_components"]
        
        new_state = state.copy()
        new_state["current_step"] = "workflow_generation_start"
        new_state["message"] = "Agent 2: Creating workflow plan..."

        try:
            system_prompt = self._get_workflow_generation_prompt()
            workflow_prompt = f"""
Problem Statement: {problem_statement}

Selected Components (full details):
{json.dumps(components_dict, indent=2)}

Generate a workflow plan to resolve this civic issue using the selected components.
"""
            
            prompt = f"{system_prompt}\n\n{workflow_prompt}"
            response = await self.llm.generate_async(prompt)
            
            response_text = self._serialize_ai_response(response.text if hasattr(response, "text") else str(response))
            workflow_json = json.loads(response_text)
            
            # Validate
            self._validate_workflow(workflow_json, components_dict)
            
            new_state["workflow_json"] = workflow_json
            new_state["current_step"] = "workflow_generation_complete"
            new_state["message"] = "Agent 2: Workflow plan created successfully"
            return new_state
        except Exception as e:
            new_state["error"] = str(e)
            return new_state

    @staticmethod
    def _get_component_selection_prompt() -> str:
        """Get the system prompt for component selection"""
        return """
You are "Mudda AI Component Selector", an expert at identifying high-level business components for civic issue resolution.

### CONTEXT
We have moved away from selecting individual API endpoints. Instead, we use **Components** which are logical units of work. 
A Component (e.g., "Plumber Service") may internally orchestrate multiple activities (e.g., LLM analysis, API call, Human approval).

### TASK
Given a problem statement, analyze the available high-level components and select ONLY the ones relevant for solving the issue.

### OUTPUT FORMAT
Respond ONLY in **valid JSON** matching this schema:

```json
{
  "selected_component_ids": ["uuid-1", "uuid-2", "uuid-3"]
}
```

### RULES:
1. Select only components that are directly relevant to solving the problem
2. Be selective - don't include unnecessary components
3. Return ONLY valid JSON with the array of selected component IDs
"""

    @staticmethod
    def _get_workflow_generation_prompt() -> str:
        """Get the system prompt for workflow generation"""
        return """
You are "Mudda AI Plan Maker", an expert government management officer and workflow automation designer.

You are part of a larger AI Orchestration System that works with Temporal.io and a "Business Component" architecture.

### CONTEXT
A **Component** is a business-level logical unit. Each component wraps one or more internal activities (e.g., LLM work, API calls, Status updates, Human approvals).
You do NOT need to orchestrate the internal activities of a component. You only orchestrate the **Components** themselves.

### TASK
Using the provided components, **design an actionable end-to-end plan** to resolve the civic issue.
The plan must follow a **directed acyclic graph (DAG)** structure, where each step references one component by `id`.

### OUTPUT FORMAT
Respond ONLY in **valid JSON** matching this schema:

```json
{
  "workflow_name": "Resolve_Water_Leakage_Issue",
  "description": "Workflow to manage and resolve a reported water leakage issue",
  "steps": [
    {
      "step_id": "fetch_issue_details",
      "component_id": "uuid-of-issue-fetch-component",
      "description": "Gather all metadata about the reported issue",
      "inputs": {
        "path_params": {"issue_id": "{{issue_id}}"}
      },
      "outputs": ["issue_details"],
      "next": ["dispatch_plumber"]
    },
    {
      "step_id": "dispatch_plumber",
      "component_id": "uuid-of-plumber-component",
      "description": "Orchestrate plumber selection and dispatch",
      "inputs": {
        "context": "{{issue_details}}"
      },
      "outputs": ["dispatch_result"],
      "next": []
    }
  ]
}
```

### RULES:
1. Use only the provided components - do not create fictional ones
2. Orchestrate at the **Component** level.
3. Every step MUST have a `component_id`.
4. Use template variables like {{issue_id}} or {{step_id.output_key}} for dynamic inputs.
5. Return ONLY valid JSON, no additional text.
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
    def _validate_workflow(workflow: Dict[str, Any], components: List[dict]) -> None:
        """Validate the generated workflow structure"""
        required_fields = ["workflow_name", "description", "steps"]
        
        for field in required_fields:
            if field not in workflow:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(workflow["steps"], list):
            raise ValueError("Steps must be a list")
        
        component_ids = {comp["id"] for comp in components}
        
        for i, step in enumerate(workflow["steps"]):
            if "step_id" not in step:
                raise ValueError(f"Step {i} missing step_id")
            if "component_id" not in step:
                raise ValueError(f"Step {i} missing component_id")
            if step["component_id"] not in component_ids:
                raise ValueError(f"Step {i} references non-existent component: {step['component_id']}")

    async def generate_workflow_plan(self, db: AsyncSession, problem_statement: str) -> Dict[str, Any]:
        """Generate a workflow plan using LangGraph"""
        initial_state = {
            "db": db,
            "problem_statement": problem_statement,
            "selected_component_ids": [],
            "selected_components": [],
            "workflow_json": {},
            "error": "",
            "current_step": "",
            "message": ""
        }
        
        final_state = await self.app.ainvoke(initial_state)
        
        if final_state.get("error"):
            raise ValueError(final_state["error"])
            
        return final_state["workflow_json"]

    async def generate_workflow_plan_stream(self, db: AsyncSession, problem_statement: str):
        """Generate a workflow plan with streaming updates using LangGraph"""
        initial_state = {
            "db": db,
            "problem_statement": problem_statement,
            "selected_component_ids": [],
            "selected_components": [],
            "workflow_json": {},
            "error": "",
            "current_step": "",
            "message": ""
        }
        
        try:
            # Use astream to get updates from each node
            async for output in self.app.astream(initial_state):
                # The output is a dict where keys are node names and values are the returned state
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
                        "agent": "component_selector" if node_name == "component_selector" else "plan_maker"
                    }
                    
                    if event_type == "component_selection_complete":
                        data["components"] = [
                            {"id": c["id"], "name": c["name"], "description": c["description"]}
                            for c in state.get("selected_components", [])
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
