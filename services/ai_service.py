"""
AI Service for workflow generation using Gemini AI
"""
import json
import re
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from services.component_service import ComponentService
from sessions.gemini_client import gemini_client


class AIService:
    """
    AI Service for generating workflow plans using Gemini AI
    """
    
    @staticmethod
    def _get_system_prompt() -> str:
        """Get the system prompt for the AI model"""
        return """
You are "Mudda AI Plan Maker", an expert government management officer and workflow automation designer.

You are part of a larger AI Orchestration System that works with Temporal.io, PostgreSQL, and REST-based microservices.
Your task is to create executable workflow plans that resolve real-world civic issues efficiently by orchestrating the use of available API components.

### CONTEXT
You will be given:
1. A **problem statement** describing a civic issue
2. A list of **available components** from the `components` table in PostgreSQL

### OBJECTIVE
Using the available components, **design an actionable end-to-end plan** to resolve the civic issue.
The plan must follow a **directed acyclic graph (DAG)** structure, where each step references one component by `id`, defines its inputs, and indicates dependencies.

The workflow must be **ready for orchestration by Temporal**, meaning:
- Each step can be executed independently by a Temporal worker
- Inputs and outputs between steps should be defined explicitly
- Include human approval steps if necessary before sensitive operations
- If external dependencies are needed, use appropriate components from the list

### OUTPUT FORMAT
Respond ONLY in **valid JSON** matching this schema:

```json
{
  "workflow_name": "Resolve_Water_Leakage_Issue",
  "description": "Workflow to manage and resolve a reported water leakage issue",
  "steps": [
    {
      "step_id": "fetch_issue",
      "component_id": "uuid-of-component",
      "description": "Fetch issue details from issue-service",
      "inputs": {
        "path_params": {"issue_id": "{{issue_id}}"},
        "query_params": {}
      },
      "outputs": ["issue_details"],
      "next": ["assign_engineer"]
    },
    {
      "step_id": "assign_engineer",
      "component_id": "uuid-of-assignment-component",
      "description": "Assign engineer from maintenance department",
      "inputs": {
        "request_body": {"issue_id": "{{issue_id}}", "department": "Water Maintenance"}
      },
      "outputs": ["assignment_confirmation"],
      "requires_approval": true,
      "next": ["notify_citizen"]
    },
    {
      "step_id": "notify_citizen",
      "component_id": "uuid-of-notification-component",
      "description": "Notify the citizen that issue is being resolved",
      "inputs": {
        "request_body": {"message": "Your issue is now assigned and under resolution."}
      },
      "outputs": [],
      "next": []
    }
  ]
}
```

### RULES:
1. Use only the provided components - do not create fictional ones
2. Ensure the workflow is logically sound and follows government processes
3. Include approval steps for sensitive operations - approval steps MUST have a component_id (use the "Approval Service - Human Review" component if available)
4. EVERY step MUST have a component_id - no exceptions
5. Make sure all step dependencies are properly defined
6. Use template variables like {{issue_id}} for dynamic inputs
7. Return ONLY valid JSON, no additional text
"""

    @staticmethod
    def _serialize_ai_response(response) -> str:
        """
        Extract and serialize JSON from AI response, handling markdown code blocks and extra text.
        
        Args:
            response: The response object from Gemini API
            
        Returns:
            Extracted JSON string ready for parsing
            
        Raises:
            ValueError: If response is empty or JSON cannot be extracted
        """
        # Extract text from response (handle different response formats)
        if hasattr(response, 'text'):
            response_text = response.text
        elif hasattr(response, 'candidates') and response.candidates:
            response_text = response.candidates[0].content.parts[0].text
        else:
            response_text = str(response)
        
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
        
        # If no JSON found, raise error
        raise ValueError(f"Could not extract JSON from AI response. Response text: {response_text[:500]}")

    @staticmethod
    def _validate_workflow(workflow: Dict[str, Any], components: List[dict]) -> None:
        """Validate the generated workflow structure"""
        required_fields = ["workflow_name", "description", "steps"]
        
        for field in required_fields:
            if field not in workflow:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(workflow["steps"], list):
            raise ValueError("Steps must be a list")
        
        # Get component IDs for validation
        component_ids = {comp["id"] for comp in components}
        
        for i, step in enumerate(workflow["steps"]):
            if "step_id" not in step:
                raise ValueError(f"Step {i} missing step_id")
            if "component_id" not in step:
                raise ValueError(f"Step {i} missing component_id")
            if step["component_id"] not in component_ids:
                raise ValueError(f"Step {i} references non-existent component: {step['component_id']}")

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
        
        if not components:
            raise ValueError("No active components available in the system")
        
        # Convert Pydantic models to dicts for JSON serialization
        components_dict = [component.model_dump() for component in components]
        
        # Create the prompt for Gemini
        issue_description_prompt = f"""
Problem Statement: {problem_statement}

Available Components:
{json.dumps(components_dict, indent=2)}

Please generate a workflow plan to resolve this civic issue using the available components.
Follow the DAG structure and ensure all steps are properly connected.
"""
        
        try:
            # Generate response using Gemini
            system_prompt = AIService._get_system_prompt()
            response = gemini_client.generate(system_prompt + "\n\n" + issue_description_prompt)
            
            # Extract and serialize JSON from response
            response_text = AIService._serialize_ai_response(response)
            print(f"Response text: {response_text}")
            
            # Parse the JSON response
            workflow_json = json.loads(response_text)
            print(f"Workflow JSON: {workflow_json}")
            
            # Validate the workflow structure
            AIService._validate_workflow(workflow_json, components_dict)
            
            return workflow_json
            
        except json.JSONDecodeError as e:
            # Log the actual response for debugging
            response_text_debug = response_text if 'response_text' in locals() else (response.text if 'response' in locals() and hasattr(response, 'text') else "No response received")
            raise ValueError(f"Failed to parse AI response as JSON: {e}. Response text: {response_text_debug[:500]}")
        except Exception as e:
            raise ValueError(f"Failed to generate workflow plan: {e}")
