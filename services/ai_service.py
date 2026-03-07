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

    async def generate_workflow_plan(
        self,
        issue_details: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate a workflow plan using LangGraph
        
        Args:
            issue_details: Structured issue details containing:
                - issue_id: Unique identifier
                - issue_category: Category (INFRASTRUCTURE, SANITATION, WATER)
                - created_at: Timestamp
                - description: Detailed description
                - location: LocationDetails dict with coordinate
                - media_urls: List of media URLs
                - title: Issue title
                
        Returns:
            Generated workflow plan as dictionary
        """
        if not issue_details:
            raise ValueError("issue_details is required")
        
        # Build enriched problem statement from issue details
        problem_text = self._build_problem_statement_from_issue(issue_details)
        
        initial_state = {
            "problem_statement": problem_text,
            "issue_details": issue_details,
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

    def _build_problem_statement_from_issue(self, issue_details: Dict[str, Any]) -> str:
        """
        Build a comprehensive problem statement from structured issue details
        
        Args:
            issue_details: Dictionary containing issue information
            
        Returns:
            Formatted problem statement string
        """
        parts = []
        
        # Title and ID
        if issue_details.get("title"):
            parts.append(f"Issue: {issue_details['title']}")
        if issue_details.get("issue_id"):
            parts.append(f"(ID: {issue_details['issue_id']})")
        
        # Category
        if issue_details.get("issue_category"):
            parts.append(f"\nCategory: {issue_details['issue_category']}")
        
        # Location - handle nested structure
        location = issue_details.get("location")
        if location:
            if isinstance(location, dict):
                # New nested structure
                location_parts = []
                if location.get("address_line") and location["address_line"] != "Not specified":
                    location_parts.append(location["address_line"])
                if location.get("city") and location["city"] != "Not specified":
                    location_parts.append(location["city"])
                if location.get("state") and location["state"] != "Not specified":
                    location_parts.append(location["state"])
                if location.get("pin_code") and location["pin_code"] != "000000":
                    location_parts.append(location["pin_code"])
                
                if location_parts:
                    parts.append(f"\nLocation: {', '.join(location_parts)}")
                
                # Add coordinates if available and not default
                coordinate = location.get("coordinate", {})
                if isinstance(coordinate, dict):
                    lat = coordinate.get("latitude", 0)
                    lon = coordinate.get("longitude", 0)
                else:
                    # Handle Coordinate object
                    lat = getattr(coordinate, 'latitude', 0)
                    lon = getattr(coordinate, 'longitude', 0)
                
                if lat != 0 or lon != 0:
                    parts.append(f"\nCoordinates: {lat}, {lon}")
            else:
                # Legacy string format
                parts.append(f"\nLocation: {location}")
        
        # Description
        if issue_details.get("description"):
            parts.append(f"\nDescription: {issue_details['description']}")
        
        # Media availability
        media_urls = issue_details.get("media_urls", [])
        if media_urls and len(media_urls) > 0:
            parts.append(f"\nMedia Available: {len(media_urls)} photo(s)/video(s)")
        
        # Timestamp
        if issue_details.get("created_at"):
            created_at = issue_details["created_at"]
            parts.append(f"\nReported: {created_at}")
        
        return " ".join(parts)

    async def generate_workflow_plan_stream(
        self, 
        issue_details: Dict[str, Any] = None
    ):
        """
        Generate a workflow plan with streaming updates using LangGraph
        
        Args:
            issue_details: Structured issue details (see generate_workflow_plan for details)
        """
        if not issue_details:
            raise ValueError("issue_details is required")
        
        # Build enriched problem statement from issue details
        problem_text = self._build_problem_statement_from_issue(issue_details)
        
        initial_state = {
            "problem_statement": problem_text,
            "issue_details": issue_details,
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
                        policies = state.get("retrieved_policies", [])
                        data["policies"] = [
                            {
                                "document_id": p.get("document_id"),
                                "heading": p.get("heading"),
                                "author": p.get("author"),
                                "text": p.get("text"),
                                "similarity_score": p.get("similarity_score"),
                                "source": p.get("source")
                            }
                            for p in policies
                        ]
                        # Add warning if no policies were retrieved
                        if len(policies) == 0:
                            data["warning"] = "No policies retrieved - RAG service may be unavailable"
                            data["rag_available"] = False
                        else:
                            data["rag_available"] = True
                    elif event_type == "activity_selection_complete":
                        data["activities"] = [
                            {"id": a["id"], "name": a["name"], "description": a["description"]}
                            for a in state.get("selected_activities", [])
                        ]
                    elif event_type == "workflow_generation_start":
                        # Emit start event for plan maker
                        data["status"] = "generating"
                        data["selected_activities_count"] = len(state.get("selected_activities", []))
                    elif event_type == "workflow_generation_complete":
                        # Emit the complete workflow plan
                        workflow = state.get("workflow_json")
                        data["workflow"] = workflow
                        data["plan_json"] = workflow  # Include plan_json for clarity
                        data["steps_count"] = len(workflow.get("steps", []))
                        data["workflow_name"] = workflow.get("workflow_name", "")
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
