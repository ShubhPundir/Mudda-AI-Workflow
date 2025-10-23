"""
Gemini AI client for workflow generation
"""
import json
import os
from typing import Dict, Any, List
import google.generativeai as genai


class GeminiClient:
    """
    Gemini AI client for generating workflow plans
    """
    
    def __init__(self):
        self.model = None
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini AI client"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def _get_system_prompt(self) -> str:
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
3. Include approval steps for sensitive operations
4. Make sure all step dependencies are properly defined
5. Use template variables like {{issue_id}} for dynamic inputs
6. Return ONLY valid JSON, no additional text
"""

    def generate_workflow_plan(self, problem_statement: str, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a workflow plan for the given problem statement
        
        Args:
            problem_statement: Description of the civic issue to resolve
            components: List of available components
            
        Returns:
            Dictionary containing the generated workflow plan
        """
        if not components:
            raise ValueError("No active components available in the system")
        
        # Create the prompt for Gemini
        prompt = f"""
Problem Statement: {problem_statement}

Available Components:
{json.dumps(components, indent=2)}

Please generate a workflow plan to resolve this civic issue using the available components.
Follow the DAG structure and ensure all steps are properly connected.
"""
        
        try:
            # Generate response using Gemini
            response = self.model.generate_content(self._get_system_prompt() + "\n\n" + prompt)
            
            # Parse the JSON response
            workflow_json = json.loads(response.text.strip())
            
            # Validate the workflow structure
            self._validate_workflow(workflow_json, components)
            
            return workflow_json
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {e}")
        except Exception as e:
            raise ValueError(f"Failed to generate workflow plan: {e}")

    def _validate_workflow(self, workflow: Dict[str, Any], components: List[dict]) -> None:
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


# Global Gemini client instance
gemini_client = GeminiClient()
