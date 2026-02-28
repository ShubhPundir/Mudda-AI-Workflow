"""
AI Service for workflow generation using Gemini AI and LangGraph orchestration
Uses structured output with Pydantic validation - zero regex extraction
Modular architecture with separate node files for maintainability
"""
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from .ai_nodes import (
    GraphState,
    activity_selector_node,
    plan_maker_node
)


class AIService:
    """
    AI Service for generating workflow plans using Gemini AI and LangGraph
    
    This service orchestrates a multi-agent workflow:
    1. Activity Selector - Analyzes problem and selects relevant activities
    2. Plan Maker - Creates detailed workflow plan from selected activities
    
    Architecture:
    - Modular nodes in services/ai_nodes/
    - Structured output with Pydantic validation
    - Zero regex extraction
    """

    def __init__(self):
        self._setup_graph()

    def _setup_graph(self):
        """
        Initialize the LangGraph state machine
        
        Graph structure:
        START -> activity_selector -> plan_maker -> END
        """
        workflow = StateGraph(GraphState)

        # Define nodes (imported from modular files)
        workflow.add_node("activity_selector", activity_selector_node)
        workflow.add_node("plan_maker", plan_maker_node)

        # Define edges
        workflow.set_entry_point("activity_selector")
        workflow.add_edge("activity_selector", "plan_maker")
        workflow.add_edge("plan_maker", END)

        self.app = workflow.compile()

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
