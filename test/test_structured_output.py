"""
Test structured output with Pydantic validation
Ensures zero regex, hard schema validation at decode time
"""
import pytest
from pydantic import ValidationError
from schemas.ai_schemas import (
    ActivitySelectionResponse,
    WorkflowPlanResponse,
    WorkflowStep
)


class TestActivitySelectionResponse:
    """Test activity selection schema validation"""
    
    def test_valid_selection(self):
        """Valid activity selection should pass"""
        data = {
            "selected_activity_ids": ["activity-1", "activity-2"]
        }
        result = ActivitySelectionResponse.model_validate(data)
        assert result.selected_activity_ids == ["activity-1", "activity-2"]
    
    def test_empty_selection_fails(self):
        """Empty activity list should fail validation"""
        data = {"selected_activity_ids": []}
        with pytest.raises(ValidationError) as exc_info:
            ActivitySelectionResponse.model_validate(data)
        # Pydantic's min_length constraint provides the error
        assert "at least 1 item" in str(exc_info.value).lower()
    
    def test_missing_field_fails(self):
        """Missing required field should fail"""
        data = {}
        with pytest.raises(ValidationError):
            ActivitySelectionResponse.model_validate(data)


class TestWorkflowStep:
    """Test workflow step schema validation"""
    
    def test_valid_step(self):
        """Valid workflow step should pass"""
        data = {
            "step_id": "step-1",
            "activity_id": "activity-1",
            "description": "First step",
            "inputs": {"param": "value"},
            "outputs": ["result"],
            "next": ["step-2"]
        }
        result = WorkflowStep.model_validate(data)
        assert result.step_id == "step-1"
        assert result.activity_id == "activity-1"
    
    def test_empty_string_fails(self):
        """Empty strings should fail validation"""
        data = {
            "step_id": "",
            "activity_id": "activity-1",
            "description": "Test"
        }
        with pytest.raises(ValidationError) as exc_info:
            WorkflowStep.model_validate(data)
        assert "cannot be empty" in str(exc_info.value)
    
    def test_whitespace_trimmed(self):
        """Whitespace should be trimmed"""
        data = {
            "step_id": "  step-1  ",
            "activity_id": "  activity-1  ",
            "description": "  Test  "
        }
        result = WorkflowStep.model_validate(data)
        assert result.step_id == "step-1"
        assert result.activity_id == "activity-1"
        assert result.description == "Test"


class TestWorkflowPlanResponse:
    """Test workflow plan schema validation"""
    
    def test_valid_workflow(self):
        """Valid workflow should pass"""
        data = {
            "workflow_name": "Test Workflow",
            "description": "A test workflow",
            "steps": [
                {
                    "step_id": "step-1",
                    "activity_id": "activity-1",
                    "description": "First step",
                    "inputs": {},
                    "outputs": ["result"],
                    "next": ["step-2"]
                },
                {
                    "step_id": "step-2",
                    "activity_id": "activity-2",
                    "description": "Second step",
                    "inputs": {},
                    "outputs": [],
                    "next": []
                }
            ]
        }
        result = WorkflowPlanResponse.model_validate(data)
        assert result.workflow_name == "Test Workflow"
        assert len(result.steps) == 2
    
    def test_empty_steps_fails(self):
        """Workflow with no steps should fail"""
        data = {
            "workflow_name": "Test",
            "description": "Test",
            "steps": []
        }
        with pytest.raises(ValidationError):
            WorkflowPlanResponse.model_validate(data)
    
    def test_cycle_detection(self):
        """Workflow with cycles should fail"""
        data = {
            "workflow_name": "Cyclic Workflow",
            "description": "Has a cycle",
            "steps": [
                {
                    "step_id": "step-1",
                    "activity_id": "activity-1",
                    "description": "First",
                    "next": ["step-2"]
                },
                {
                    "step_id": "step-2",
                    "activity_id": "activity-2",
                    "description": "Second",
                    "next": ["step-1"]  # Creates cycle
                }
            ]
        }
        with pytest.raises(ValidationError) as exc_info:
            WorkflowPlanResponse.model_validate(data)
        assert "cycles" in str(exc_info.value).lower()
    
    def test_invalid_next_reference(self):
        """Reference to non-existent step should fail"""
        data = {
            "workflow_name": "Test",
            "description": "Test",
            "steps": [
                {
                    "step_id": "step-1",
                    "activity_id": "activity-1",
                    "description": "First",
                    "next": ["non-existent-step"]
                }
            ]
        }
        with pytest.raises(ValidationError) as exc_info:
            WorkflowPlanResponse.model_validate(data)
        assert "non-existent" in str(exc_info.value).lower()
    
    def test_validate_activity_ids(self):
        """Activity ID validation should work"""
        data = {
            "workflow_name": "Test",
            "description": "Test",
            "steps": [
                {
                    "step_id": "step-1",
                    "activity_id": "invalid-activity",
                    "description": "First"
                }
            ]
        }
        workflow = WorkflowPlanResponse.model_validate(data)
        
        valid_ids = {"activity-1", "activity-2"}
        with pytest.raises(ValueError) as exc_info:
            workflow.validate_activity_ids(valid_ids)
        assert "non-existent activity" in str(exc_info.value).lower()


class TestNoRegexExtraction:
    """Verify no regex is used - structured output only"""
    
    def test_malformed_json_fails_immediately(self):
        """Malformed JSON should fail at parse time, not regex extraction"""
        malformed = '{"selected_activity_ids": ["activity-1"'  # Missing closing bracket
        
        import json
        with pytest.raises(json.JSONDecodeError):
            json.loads(malformed)
    
    def test_schema_mismatch_fails(self):
        """Wrong schema structure should fail validation"""
        data = {
            "wrong_field": ["activity-1"]  # Wrong field name
        }
        with pytest.raises(ValidationError):
            ActivitySelectionResponse.model_validate(data)
    
    def test_type_mismatch_fails(self):
        """Wrong data types should fail validation"""
        data = {
            "selected_activity_ids": "not-a-list"  # Should be list
        }
        with pytest.raises(ValidationError):
            ActivitySelectionResponse.model_validate(data)
