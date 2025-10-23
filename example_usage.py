"""
Example usage and test cases for Mudda AI Workflow system
"""
import asyncio
import json
from datetime import datetime
from sqlalchemy.orm import Session
from sessions.database import SessionLocal, engine
from models import Base, Component
from services import ComponentService, WorkflowService
from temporal_workflows import execute_workflow_plan


def create_sample_components():
    """Create sample components for testing"""
    db = SessionLocal()
    try:
        # Check if components already exist
        if db.query(Component).count() > 0:
            print("Sample components already exist")
            return
        
        # Create sample components
        components = [
            {
                "name": "Issue Service - Get Issue Details",
                "description": "Fetch detailed information about a reported issue",
                "type": "REST",
                "category": "Issue Management",
                "endpoint_url": "https://issue-service.gov/api/issues/{issue_id}",
                "http_method": "GET",
                "request_schema": None,
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "issue_id": {"type": "string"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "location": {"type": "string"},
                        "priority": {"type": "string"},
                        "status": {"type": "string"}
                    }
                },
                "path_params": {"issue_id": "string"},
                "query_params": {},
                "owner_service": "issue-service"
            },
            {
                "name": "Assignment Service - Assign Officer",
                "description": "Assign an officer to handle the issue",
                "type": "REST",
                "category": "Assignment",
                "endpoint_url": "https://assignment-service.gov/api/assignments",
                "http_method": "POST",
                "request_schema": {
                    "type": "object",
                    "properties": {
                        "issue_id": {"type": "string"},
                        "department": {"type": "string"},
                        "priority": {"type": "string"}
                    },
                    "required": ["issue_id", "department"]
                },
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "assignment_id": {"type": "string"},
                        "officer_id": {"type": "string"},
                        "assigned_at": {"type": "string"}
                    }
                },
                "path_params": {},
                "query_params": {},
                "owner_service": "assignment-service"
            },
            {
                "name": "Notification Service - Send SMS",
                "description": "Send SMS notification to citizen",
                "type": "REST",
                "category": "Notification",
                "endpoint_url": "https://notification-service.gov/api/sms",
                "http_method": "POST",
                "request_schema": {
                    "type": "object",
                    "properties": {
                        "phone_number": {"type": "string"},
                        "message": {"type": "string"}
                    },
                    "required": ["phone_number", "message"]
                },
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "message_id": {"type": "string"},
                        "status": {"type": "string"}
                    }
                },
                "path_params": {},
                "query_params": {},
                "owner_service": "notification-service"
            },
            {
                "name": "Work Order Service - Create Work Order",
                "description": "Create a work order for maintenance tasks",
                "type": "REST",
                "category": "Work Management",
                "endpoint_url": "https://workorder-service.gov/api/work-orders",
                "http_method": "POST",
                "request_schema": {
                    "type": "object",
                    "properties": {
                        "issue_id": {"type": "string"},
                        "assigned_officer": {"type": "string"},
                        "work_type": {"type": "string"},
                        "priority": {"type": "string"},
                        "estimated_duration": {"type": "string"}
                    },
                    "required": ["issue_id", "assigned_officer", "work_type"]
                },
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "work_order_id": {"type": "string"},
                        "status": {"type": "string"},
                        "created_at": {"type": "string"}
                    }
                },
                "path_params": {},
                "query_params": {},
                "owner_service": "workorder-service"
            },
            {
                "name": "Status Service - Update Issue Status",
                "description": "Update the status of an issue",
                "type": "REST",
                "category": "Status Management",
                "endpoint_url": "https://status-service.gov/api/issues/{issue_id}/status",
                "http_method": "PUT",
                "request_schema": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "notes": {"type": "string"}
                    },
                    "required": ["status"]
                },
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "issue_id": {"type": "string"},
                        "status": {"type": "string"},
                        "updated_at": {"type": "string"}
                    }
                },
                "path_params": {"issue_id": "string"},
                "query_params": {},
                "owner_service": "status-service"
            }
        ]
        
        for comp_data in components:
            component = Component(**comp_data)
            db.add(component)
        
        db.commit()
        print(f"Created {len(components)} sample components")
        
    except Exception as e:
        print(f"Error creating sample components: {e}")
        db.rollback()
    finally:
        db.close()


def test_workflow_generation():
    """Test workflow generation with sample problem statements"""
    db = SessionLocal()
    try:
        workflow_service = WorkflowService(db)
        
        # Test problem statements
        test_cases = [
            "Resolve pothole issue reported in Ward 22",
            "Fix water leakage in Sector 5 residential area",
            "Address street light malfunction on Main Road",
            "Clear garbage accumulation in Park Street area",
            "Repair damaged traffic signal at Central Junction"
        ]
        
        print("Testing workflow generation...")
        print("=" * 50)
        
        for i, problem in enumerate(test_cases, 1):
            print(f"\nTest Case {i}: {problem}")
            print("-" * 30)
            
            try:
                from schemas import ProblemStatementRequest
                request = ProblemStatementRequest(problem_statement=problem)
                result = workflow_service.generate_workflow(request)
                
                print(f"✅ Generated workflow: {result.workflow_plan.workflow_name}")
                print(f"   Workflow ID: {result.workflow_id}")
                print(f"   Number of steps: {len(result.workflow_plan.steps)}")
                
                # Print step details
                for j, step in enumerate(result.workflow_plan.steps, 1):
                    print(f"   Step {j}: {step.step_id} -> {step.description}")
                
            except Exception as e:
                print(f"❌ Failed to generate workflow: {e}")
        
    finally:
        db.close()


async def test_workflow_execution():
    """Test workflow execution with Temporal"""
    print("\nTesting workflow execution...")
    print("=" * 50)
    
    # Sample workflow plan
    sample_workflow = {
        "workflow_name": "Test_Pothole_Resolution",
        "description": "Test workflow for pothole resolution",
        "steps": [
            {
                "step_id": "fetch_issue",
                "component_id": "sample-component-id",
                "description": "Fetch issue details",
                "inputs": {"path_params": {"issue_id": "{{issue_id}}"}},
                "outputs": ["issue_details"],
                "next": ["assign_officer"]
            },
            {
                "step_id": "assign_officer",
                "component_id": "sample-component-id",
                "description": "Assign officer to issue",
                "inputs": {"request_body": {"issue_id": "{{issue_id}}", "department": "Road Maintenance"}},
                "outputs": ["assignment_confirmation"],
                "requires_approval": True,
                "next": ["notify_citizen"]
            },
            {
                "step_id": "notify_citizen",
                "component_id": "sample-component-id",
                "description": "Notify citizen about assignment",
                "inputs": {"request_body": {"message": "Your issue has been assigned and is being resolved."}},
                "outputs": [],
                "next": []
            }
        ]
    }
    
    try:
        # Note: This would require a running Temporal server
        # workflow_id = await execute_workflow_plan(sample_workflow, "test-execution-123")
        # print(f"✅ Started workflow execution: {workflow_id}")
        print("⚠️  Workflow execution test requires running Temporal server")
        print("   To test: Start Temporal server and uncomment the execution code")
        
    except Exception as e:
        print(f"❌ Failed to execute workflow: {e}")


def test_api_endpoints():
    """Test API endpoints using HTTP requests"""
    import requests
    import json
    
    base_url = "http://localhost:8000"
    
    print("\nTesting API endpoints...")
    print("=" * 50)
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test component listing
    try:
        response = requests.get(f"{base_url}/components")
        if response.status_code == 200:
            components = response.json()
            print(f"✅ Found {len(components)} components")
        else:
            print(f"❌ Failed to list components: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to list components: {e}")
    
    # Test workflow generation
    try:
        payload = {
            "problem_statement": "Test pothole issue in Ward 1"
        }
        response = requests.post(
            f"{base_url}/workflows/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Generated workflow: {result['workflow_plan']['workflow_name']}")
        else:
            print(f"❌ Failed to generate workflow: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to generate workflow: {e}")


def main():
    """Main function to run all tests"""
    print("Mudda AI Workflow System - Example Usage")
    print("=" * 60)
    
    # Create database tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    # Create sample components
    print("\nCreating sample components...")
    create_sample_components()
    
    # Test workflow generation
    print("\nTesting workflow generation...")
    test_workflow_generation()
    
    # Test workflow execution
    print("\nTesting workflow execution...")
    asyncio.run(test_workflow_execution())
    
    # Test API endpoints (requires running server)
    print("\nTesting API endpoints...")
    print("⚠️  Make sure to start the API server first:")
    print("   python main.py")
    test_api_endpoints()
    
    print("\n" + "=" * 60)
    print("Example usage completed!")
    print("\nTo start the API server:")
    print("  python main.py")
    print("\nTo start the Temporal worker:")
    print("  python temporal_worker.py")


if __name__ == "__main__":
    main()