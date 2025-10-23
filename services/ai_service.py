"""
AI Service for workflow generation using Gemini AI
"""
from typing import Dict, Any
from services.component_service import ComponentService
from sessions.gemini_client import gemini_client


class AIService:
    """
    AI Service for generating workflow plans using Gemini AI
    """
    
    def __init__(self, component_service: ComponentService):
        self.component_service = component_service
        self.gemini_client = gemini_client

    def generate_workflow_plan(self, problem_statement: str) -> Dict[str, Any]:
        """
        Generate a workflow plan for the given problem statement
        
        Args:
            problem_statement: Description of the civic issue to resolve
            
        Returns:
            Dictionary containing the generated workflow plan
        """
        # Get available components
        components = self.component_service.get_components_for_ai()
        
        # Use the Gemini client to generate the workflow
        return self.gemini_client.generate_workflow_plan(problem_statement, components)
