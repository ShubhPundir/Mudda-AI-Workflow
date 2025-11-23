"""
AI Service for workflow generation using Gemini AI
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from services.component_service import ComponentService
from sessions.gemini_client import gemini_client


class AIService:
    """
    AI Service for generating workflow plans using Gemini AI
    """
    
    @staticmethod
    def generate_workflow_plan(db: Session, problem_statement: str) -> Dict[str, Any]:
        """
        Generate a workflow plan for the given problem statement
        
        Args:
            db: Database session
            problem_statement: Description of the civic issue to resolve
            
        Returns:
            Dictionary containing the generated workflow plan
        """
        # Get available components
        components = ComponentService.get_components_for_ai(db)
        # Use the Gemini client to generate the workflow
        return gemini_client.generate_workflow_plan(problem_statement, components)
