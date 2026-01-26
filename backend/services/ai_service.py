"""
AI Service for workflow generation using Gemini AI
"""
import json
import re
from typing import Dict, Any, List
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from services.component_service import ComponentService
from sessions.gemini_client import gemini_client


class AIService:
    """
    AI Service for generating workflow plans using Gemini AI
    """
    
    @staticmethod
    def _get_component_selection_prompt() -> str:
        """Get the system prompt for component selection"""
        return """
You are "Mudda AI Component Selector", an expert at identifying relevant API components for civic issue resolution.

### TASK
Given a problem statement, analyze the available components and select ONLY the components that are relevant for solving the issue.

### OUTPUT FORMAT
Respond ONLY in **valid JSON** matching this schema:

```json
{
  "selected_component_ids": ["uuid-1", "uuid-2", "uuid-3"]
}
```

### RULES:
1. Select only components that are directly relevant to solving the problem
2. Include components for: issue management, notifications, approvals, external services, etc.
3. Be selective - don't include unnecessary components
4. Return ONLY valid JSON with the array of selected component IDs
"""

    @staticmethod
    def _get_workflow_generation_prompt() -> str:
        """Get the system prompt for workflow generation"""
        return """
You are "Mudda AI Plan Maker", an expert government management officer and workflow automation designer.

You are part of a larger AI Orchestration System that works with Temporal.io, PostgreSQL, and REST-based microservices.
Your task is to create executable workflow plans that resolve real-world civic issues efficiently by orchestrating the use of available API components.

### CONTEXT
You will be given:
1. A **problem statement** describing a civic issue
2. A list of **selected components** with full details (endpoint URLs, schemas, etc.)

### OBJECTIVE
Using the provided components, **design an actionable end-to-end plan** to resolve the civic issue.
The plan must follow a **directed acyclic graph (DAG)** structure, where each step references one component by `id`, defines its inputs, and indicates dependencies.

The workflow must be **ready for orchestration by Temporal**, meaning:
- Each step can be executed independently by a Temporal worker
- Inputs and outputs between steps should be defined explicitly
- Include human approval steps if necessary before sensitive operations
- Use the exact endpoint URLs, HTTP methods, and schemas from the provided components

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
7. Use the exact endpoint URLs, HTTP methods, and request/response schemas from the component details
8. Return ONLY valid JSON, no additional text
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
    async def select_components(db: AsyncSession, problem_statement: str) -> List[str]:
        """
        Step 1: Select relevant components for the problem statement
        
        Args:
            db: Database session
            problem_statement: Description of the civic issue to resolve
            
        Returns:
            List of selected component IDs
        """
        # Get minimal component info (id, name, description only)
        components = await ComponentService.get_components_for_selection(db)
        
        if not components:
            raise ValueError("No active components available in the system")
        
        # Convert to dicts for JSON serialization
        components_dict = [component.model_dump() for component in components]
        
        # Create the prompt for component selection
        selection_prompt = f"""
Problem Statement: {problem_statement}

Available Components (minimal info):
{json.dumps(components_dict, indent=2)}

Select the component IDs that are relevant for solving this problem.
"""
        
        try:
            # Generate response using Gemini
            system_prompt = AIService._get_component_selection_prompt()
            response = await gemini_client.generate_async(system_prompt + "\n\n" + selection_prompt)
            
            # Extract and serialize JSON from response
            response_text = AIService._serialize_ai_response(response)
            
            # Parse the JSON response
            selection_result = json.loads(response_text)
            
            if "selected_component_ids" not in selection_result:
                raise ValueError("AI response missing 'selected_component_ids' field")
            
            selected_ids = selection_result["selected_component_ids"]
            
            if not isinstance(selected_ids, list) or len(selected_ids) == 0:
                raise ValueError("No components were selected")
            
            return selected_ids
            
        except json.JSONDecodeError as e:
            response_text_debug = response_text if 'response_text' in locals() else "No response received"
            raise ValueError(f"Failed to parse component selection response as JSON: {e}. Response text: {response_text_debug[:500]}")
        except Exception as e:
            raise ValueError(f"Failed to select components: {e}")

    @staticmethod
    async def generate_workflow_plan(db: AsyncSession, problem_statement: str) -> Dict[str, Any]:
        """
        Generate a workflow plan for the given problem statement using two-step process:
        1. Select relevant components (minimal token usage)
        2. Generate workflow with full component details
        
        Args:
            db: Database session
            problem_statement: Description of the civic issue to resolve
            
        Returns:
            Dictionary containing the generated workflow plan
        """
        # Step 1: Select relevant components
        print("Step 1: Selecting relevant components...")
        selected_component_ids = await AIService.select_components(db, problem_statement)
        print(f"Selected {len(selected_component_ids)} components: {selected_component_ids}")
        
        # Step 2: Get full details for selected components only
        selected_components = await ComponentService.get_components_by_ids(db, selected_component_ids)
        
        if not selected_components:
            raise ValueError("Failed to retrieve details for selected components")
        
        # Convert to dicts for JSON serialization
        components_dict = [component.model_dump() for component in selected_components]
        
        # Create the prompt for workflow generation
        workflow_prompt = f"""
Problem Statement: {problem_statement}

Selected Components (full details):
{json.dumps(components_dict, indent=2)}

Generate a workflow plan to resolve this civic issue using the selected components.
Follow the DAG structure and ensure all steps are properly connected.
Use the exact endpoint URLs, HTTP methods, and schemas from the component details.
"""
        
        try:
            # Generate response using Gemini
            system_prompt = AIService._get_workflow_generation_prompt()
            response = await gemini_client.generate_async(system_prompt + "\n\n" + workflow_prompt)
            
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
    
    @staticmethod
    async def generate_workflow_plan_stream(db: AsyncSession, problem_statement: str):
        """
        Generate a workflow plan with streaming progress updates.
        Yields SSE-compatible events at each stage.
        
        Args:
            db: Database session
            problem_statement: Description of the civic issue to resolve
            
        Yields:
            Dict containing event type and data for SSE streaming
        """
        try:
            # Step 1: Component Selection Start
            yield {
                "event": "component_selection_start",
                "data": {
                    "message": "Agent 1: Analyzing problem and selecting components...",
                    "agent": "component_selector"
                }
            }
            
            # Select relevant components
            selected_component_ids = await AIService.select_components(db, problem_statement)
            
            # Step 2: Get full details for selected components
            selected_components = await ComponentService.get_components_by_ids(db, selected_component_ids)
            
            if not selected_components:
                raise ValueError("Failed to retrieve details for selected components")
            
            # Convert to dicts for JSON serialization
            components_dict = [component.model_dump() for component in selected_components]
            
            # Yield component selection complete with component details
            yield {
                "event": "component_selection_complete",
                "data": {
                    "message": f"Agent 1: Selected {len(components_dict)} components",
                    "agent": "component_selector",
                    "components": [
                        {
                            "id": comp["id"],
                            "name": comp["name"],
                            "description": comp["description"]
                        }
                        for comp in components_dict
                    ]
                }
            }
            
            # Step 3: Workflow Generation Start
            yield {
                "event": "workflow_generation_start",
                "data": {
                    "message": "Agent 2: Creating workflow plan...",
                    "agent": "plan_maker"
                }
            }
            
            # Create the prompt for workflow generation
            workflow_prompt = f"""
Problem Statement: {problem_statement}

Selected Components (full details):
{json.dumps(components_dict, indent=2)}

Generate a workflow plan to resolve this civic issue using the selected components.
Follow the DAG structure and ensure all steps are properly connected.
Use the exact endpoint URLs, HTTP methods, and schemas from the component details.
"""
            
            # Generate response using Gemini
            system_prompt = AIService._get_workflow_generation_prompt()
            response = await gemini_client.generate_async(system_prompt + "\n\n" + workflow_prompt)
            
            # Extract and serialize JSON from response
            response_text = AIService._serialize_ai_response(response)
            
            # Parse the JSON response
            workflow_json = json.loads(response_text)
            
            # Validate the workflow structure
            AIService._validate_workflow(workflow_json, components_dict)
            
            # Step 4: Workflow Generation Complete
            yield {
                "event": "workflow_generation_complete",
                "data": {
                    "message": "Agent 2: Workflow plan created successfully",
                    "agent": "plan_maker",
                    "workflow": workflow_json
                }
            }
            
        except Exception as e:
            yield {
                "event": "error",
                "data": {
                    "message": str(e),
                    "error": True
                }
            }
