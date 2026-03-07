"""
Plan Validator Node for LangGraph workflow
Validates workflow plans for reliability and correctness
"""
from typing import Dict, Any, List, Set
from .graph_state import GraphState


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class PlanValidator:
    """
    Comprehensive workflow plan validator
    
    Checks:
    - Cycle detection (DAG validation)
    - Missing inputs
    - Orphan nodes (unreachable steps)
    - Unused activities
    - SLA coverage
    """
    
    def __init__(self, workflow_json: Dict[str, Any], selected_activities: List[Dict[str, Any]]):
        self.workflow = workflow_json
        self.selected_activities = selected_activities
        self.steps = workflow_json.get("steps", [])
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self) -> Dict[str, Any]:
        """
        Run all validation checks
        
        Returns:
            Dict with validation results
        """
        self._check_cycles()
        self._check_missing_inputs()
        self._check_orphan_nodes()
        self._check_unused_activities()
        self._check_sla_coverage()
        
        return {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings
        }
    
    def _check_cycles(self):
        """
        Check for cycles in the workflow DAG
        Uses DFS-based cycle detection
        """
        if not self.steps:
            self.errors.append("Workflow has no steps")
            return
        
        # Build adjacency list
        adjacency = {step["step_id"]: step.get("next", []) for step in self.steps}
        visited = set()
        rec_stack = set()
        
        def has_cycle(node: str, path: List[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in adjacency.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, path + [neighbor]):
                        return True
                elif neighbor in rec_stack:
                    cycle_path = " -> ".join(path + [neighbor])
                    self.errors.append(f"Cycle detected: {cycle_path}")
                    return True
            
            rec_stack.remove(node)
            return False
        
        # Check for cycles starting from each unvisited node
        for step in self.steps:
            step_id = step["step_id"]
            if step_id not in visited:
                has_cycle(step_id, [step_id])
    
    def _check_missing_inputs(self):
        """
        Check for missing or undefined inputs in workflow steps
        Validates that template variables reference valid outputs
        """
        # Collect all outputs from all steps
        available_outputs = set()
        for step in self.steps:
            step_id = step["step_id"]
            outputs = step.get("outputs", [])
            for output in outputs:
                available_outputs.add(f"{step_id}.{output}")
        
        # Check each step's inputs
        for step in self.steps:
            step_id = step["step_id"]
            inputs = step.get("inputs", {})
            
            for input_name, input_value in inputs.items():
                if isinstance(input_value, str):
                    # Check for template variables like {{step_id.output}}
                    if "{{" in input_value and "}}" in input_value:
                        # Extract variable name
                        start = input_value.find("{{") + 2
                        end = input_value.find("}}")
                        var_name = input_value[start:end].strip()
                        
                        # Check if it references a step output
                        if "." in var_name:
                            if var_name not in available_outputs:
                                self.errors.append(
                                    f"Step '{step_id}' input '{input_name}' references "
                                    f"undefined output: {var_name}"
                                )
                        # Check if it's a workflow input
                        elif var_name not in ["problem_statement", "issue_id", "citizen_id"]:
                            self.warnings.append(
                                f"Step '{step_id}' input '{input_name}' references "
                                f"variable '{var_name}' - ensure it's provided at runtime"
                            )
    
    def _check_orphan_nodes(self):
        """
        Check for orphan nodes (steps that are unreachable from entry points)
        """
        if not self.steps:
            return
        
        # Find entry points (steps with no incoming edges)
        step_ids = {step["step_id"] for step in self.steps}
        has_incoming = set()
        
        for step in self.steps:
            for next_id in step.get("next", []):
                has_incoming.add(next_id)
        
        entry_points = step_ids - has_incoming
        
        if not entry_points:
            self.errors.append("No entry points found - all steps have incoming edges (cycle?)")
            return
        
        # BFS to find all reachable nodes
        reachable = set()
        queue = list(entry_points)
        
        while queue:
            current = queue.pop(0)
            if current in reachable:
                continue
            reachable.add(current)
            
            # Find step and add its next nodes
            for step in self.steps:
                if step["step_id"] == current:
                    for next_id in step.get("next", []):
                        if next_id not in reachable:
                            queue.append(next_id)
                    break
        
        # Check for orphans
        orphans = step_ids - reachable
        if orphans:
            orphan_list = ", ".join(sorted(orphans))
            self.errors.append(f"Orphan nodes detected (unreachable): {orphan_list}")
    
    def _check_unused_activities(self):
        """
        Check if all selected activities are used in the workflow
        Warns about activities that were selected but not used
        """
        selected_activity_ids = {act["id"] for act in self.selected_activities}
        used_activity_ids = {step["activity_id"] for step in self.steps}
        
        unused = selected_activity_ids - used_activity_ids
        if unused:
            unused_list = ", ".join(sorted(unused))
            self.warnings.append(
                f"Selected activities not used in workflow: {unused_list}"
            )
        
        # Also check for activities used but not selected (should not happen with structured output)
        not_selected = used_activity_ids - selected_activity_ids
        if not_selected:
            not_selected_list = ", ".join(sorted(not_selected))
            self.errors.append(
                f"Workflow uses activities that were not selected: {not_selected_list}"
            )
    
    def _check_sla_coverage(self):
        """
        Check for SLA coverage in workflow
        Ensures critical steps have SLA considerations
        """
        # Check if workflow has description
        if not self.workflow.get("description"):
            self.warnings.append("Workflow missing description")
        
        # Check for terminal nodes (steps with no next)
        terminal_nodes = [
            step["step_id"] 
            for step in self.steps 
            if not step.get("next")
        ]
        
        if not terminal_nodes:
            self.warnings.append("No terminal nodes found - workflow may not complete properly")
        elif len(terminal_nodes) > 1:
            terminal_list = ", ".join(terminal_nodes)
            self.warnings.append(
                f"Multiple terminal nodes found: {terminal_list}. "
                "Consider consolidating to a single completion step."
            )
        
        # Check for notification/communication steps
        has_notification = any(
            "notif" in step.get("activity_id", "").lower() or
            "email" in step.get("activity_id", "").lower() or
            "sms" in step.get("activity_id", "").lower()
            for step in self.steps
        )
        
        if not has_notification:
            self.warnings.append(
                "No notification/communication step found. "
                "Consider adding citizen notification for better service."
            )
        
        # Check for human approval steps in critical workflows
        has_approval = any(
            "approv" in step.get("activity_id", "").lower() or
            "human" in step.get("activity_id", "").lower()
            for step in self.steps
        )
        
        # Only warn if workflow has more than 3 steps (complex workflow)
        if len(self.steps) > 3 and not has_approval:
            self.warnings.append(
                "Complex workflow without human approval step. "
                "Consider adding approval for quality control."
            )


async def plan_validator_node(state: GraphState) -> GraphState:
    """
    Node for validating workflow plans
    
    This node:
    1. Takes the generated workflow plan
    2. Runs comprehensive validation checks
    3. Returns updated state with validation results
    4. Sets error if validation fails
    
    Validation checks:
    - Cycle detection (DAG validation)
    - Missing inputs
    - Orphan nodes (unreachable steps)
    - Unused activities
    - SLA coverage
    
    Args:
        state: Current graph state containing workflow_json
        
    Returns:
        Updated graph state with validation results
    """
    # Early return if there's an error from previous node
    if state.get("error"):
        return state
    
    workflow_json = state.get("workflow_json")
    selected_activities = state.get("selected_activities", [])
    
    new_state = state.copy()
    new_state["current_step"] = "plan_validation_start"
    new_state["message"] = "Agent 3: Validating workflow plan..."
    
    try:
        # Validate workflow
        validator = PlanValidator(workflow_json, selected_activities)
        validation_result = validator.validate()
        
        # Store validation results in state
        new_state["validation_result"] = validation_result
        
        if not validation_result["valid"]:
            # Validation failed - set error
            error_msg = "Workflow validation failed:\n" + "\n".join(
                f"  - {error}" for error in validation_result["errors"]
            )
            new_state["error"] = error_msg
            new_state["current_step"] = "plan_validation_failed"
            new_state["message"] = "Agent 3: Validation failed"
        else:
            # Validation passed
            new_state["current_step"] = "plan_validation_complete"
            
            # Build message with warnings if any
            if validation_result["warnings"]:
                warning_count = len(validation_result["warnings"])
                new_state["message"] = (
                    f"Agent 3: Validation passed with {warning_count} warning(s)"
                )
            else:
                new_state["message"] = "Agent 3: Validation passed - workflow is valid"
        
        return new_state
        
    except Exception as e:
        new_state["error"] = f"Validation error: {str(e)}"
        new_state["current_step"] = "plan_validation_error"
        return new_state
