"""
AI Service for workflow generation using Gemini AI and LangGraph orchestration
Uses structured output with Pydantic validation - zero regex extraction
Modular architecture with separate node files for maintainability
"""
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from .ai_nodes import (
    GraphState,
    policy_retrieval_node,
    activity_selector_node,
    plan_maker_node,
    plan_validator_node
)


class AIService:
    """
    AI Service for generating workflow plans using Gemini AI and LangGraph
    
    This service orchestrates a multi-agent workflow:
    1. Policy Retrieval - Retrieves relevant policies from knowledge base using RAG
    2. Activity Selector - Analyzes problem and selects relevant activities
    3. Plan Maker - Creates detailed workflow plan from selected activities
    4. Plan Validator - Validates workflow for reliability and correctness
    
    Architecture:
    - Modular nodes in services/ai_nodes/
    - Structured output with Pydantic validation
    - Zero regex extraction
    - Comprehensive plan validation
    - RAG-powered policy retrieval
    """

    def __init__(self):
        self._setup_graph()

    def _setup_graph(self):
        """
        Initialize the LangGraph state machine
        
        Graph structure:
        START -> policy_retrieval -> activity_selector -> plan_maker -> plan_validator -> END
        """
        workflow = StateGraph(GraphState)

        # Define nodes (imported from modular files)
        workflow.add_node("policy_retrieval", policy_retrieval_node) # RAG
        workflow.add_node("activity_selector", activity_selector_node)
        workflow.add_node("plan_maker", plan_maker_node) # FIX via usage of compiler
        workflow.add_node("plan_validator", plan_validator_node)

        # Define edges
        workflow.set_entry_point("policy_retrieval")
        workflow.add_edge("policy_retrieval", "activity_selector")
        workflow.add_edge("activity_selector", "plan_maker")
        workflow.add_edge("plan_maker", "plan_validator")
        workflow.add_edge("plan_validator", END)

        self.app = workflow.compile()

    async def generate_workflow_plan(self, problem_statement: str) -> Dict[str, Any]:
        """Generate a workflow plan using LangGraph"""
        initial_state = {
            "problem_statement": problem_statement,
            "retrieved_policies": [],
            "selected_activity_ids": [],
            "selected_activities": [],
            "workflow_json": {},
            "validation_result": {},
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
            "retrieved_policies": [],
            "selected_activity_ids": [],
            "selected_activities": [],
            "workflow_json": {},
            "validation_result": {},
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
                        "agent": self._get_agent_name(node_name)
                    }
                    
                    if event_type == "policy_retrieval_complete":
                        data["policies"] = [
                            {"heading": p["heading"], "author": p["author"], "similarity_score": p["similarity_score"]}
                            for p in state.get("retrieved_policies", [])
                        ]
                    elif event_type == "activity_selection_complete":
                        data["activities"] = [
                            {"id": a["id"], "name": a["name"], "description": a["description"]}
                            for a in state.get("selected_activities", [])
                        ]
                    elif event_type == "workflow_generation_complete":
                        data["workflow"] = state.get("workflow_json")
                    elif event_type == "plan_validation_complete":
                        data["validation"] = state.get("validation_result")
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
    
    def _get_agent_name(self, node_name: str) -> str:
        """Map node name to agent name for streaming"""
        mapping = {
            "policy_retrieval": "policy_retrieval",
            "activity_selector": "activity_selector",
            "plan_maker": "plan_maker",
            "plan_validator": "plan_validator"
        }
        return mapping.get(node_name, node_name)


# Global AI service instance
ai_service = AIService()
