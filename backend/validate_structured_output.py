#!/usr/bin/env python3
"""
Quick validation script to verify structured output implementation
"""
import sys

def validate_imports():
    """Validate all imports work correctly"""
    print("Validating imports...")
    
    try:
        from schemas.ai_schemas import (
            ActivitySelectionResponse,
            WorkflowPlanResponse,
            WorkflowStep
        )
        print("✓ AI schemas imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import AI schemas: {e}")
        return False
    
    try:
        from sessions.llm.llm_interface import LLMInterface
        print("✓ LLM interface imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import LLM interface: {e}")
        return False
    
    try:
        from sessions.llm.gemini_LLM_adapter import GeminiLLMAdapter
        print("✓ Gemini adapter imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Gemini adapter: {e}")
        return False
    
    try:
        from services.ai_service import AIService
        print("✓ AI service imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import AI service: {e}")
        return False
    
    return True


def validate_schemas():
    """Validate schema definitions work correctly"""
    print("\nValidating schemas...")
    
    from schemas.ai_schemas import (
        ActivitySelectionResponse,
        WorkflowPlanResponse,
        WorkflowStep
    )
    
    # Test ActivitySelectionResponse
    try:
        response = ActivitySelectionResponse(
            selected_activity_ids=["activity-1", "activity-2"]
        )
        assert response.selected_activity_ids == ["activity-1", "activity-2"]
        print("✓ ActivitySelectionResponse validation works")
    except Exception as e:
        print(f"✗ ActivitySelectionResponse validation failed: {e}")
        return False
    
    # Test WorkflowStep
    try:
        step = WorkflowStep(
            step_id="step-1",
            activity_id="activity-1",
            description="Test step"
        )
        assert step.step_id == "step-1"
        print("✓ WorkflowStep validation works")
    except Exception as e:
        print(f"✗ WorkflowStep validation failed: {e}")
        return False
    
    # Test WorkflowPlanResponse
    try:
        workflow = WorkflowPlanResponse(
            workflow_name="Test Workflow",
            description="A test workflow",
            steps=[
                WorkflowStep(
                    step_id="step-1",
                    activity_id="activity-1",
                    description="First step"
                )
            ]
        )
        assert workflow.workflow_name == "Test Workflow"
        print("✓ WorkflowPlanResponse validation works")
    except Exception as e:
        print(f"✗ WorkflowPlanResponse validation failed: {e}")
        return False
    
    return True


def validate_interface():
    """Validate LLM interface has structured output method"""
    print("\nValidating LLM interface...")
    
    from sessions.llm.llm_interface import LLMInterface
    import inspect
    
    # Check if generate_structured method exists
    if hasattr(LLMInterface, 'generate_structured'):
        sig = inspect.signature(LLMInterface.generate_structured)
        params = list(sig.parameters.keys())
        if 'content' in params and 'response_schema' in params:
            print("✓ LLM interface has generate_structured method with correct signature")
            return True
        else:
            print(f"✗ generate_structured has wrong parameters: {params}")
            return False
    else:
        print("✗ LLM interface missing generate_structured method")
        return False


def main():
    """Run all validations"""
    print("=" * 60)
    print("STRUCTURED OUTPUT VALIDATION")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", validate_imports()))
    results.append(("Schemas", validate_schemas()))
    results.append(("Interface", validate_interface()))
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:20} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All validations passed!")
        print("\nNext steps:")
        print("  1. Run tests: pytest backend/test/test_structured_output.py")
        print("  2. Try example: python backend/example/structured_output_example.py")
        return 0
    else:
        print("\n✗ Some validations failed. Check errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
