"""
Simple Workflow Example (No Database Required)

This example runs a workflow without requiring database setup.
It demonstrates the core workflow execution without DB dependencies.

Usage:
    cd backend
    python example/simple_workflow_no_db.py
"""
import asyncio
import logging
import sys
import uuid
from pathlib import Path
from typing import Dict, Any

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from temporalio.client import Client
from temporalio import workflow
from temporalio.worker import Worker
from datetime import timedelta

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Simple workflow without database dependencies
@workflow.defn
class SimpleTestWorkflow:
    """Simple workflow for testing without database."""
    
    def __init__(self):
        self.results = {}
    
    @workflow.run
    async def run(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a simple test workflow."""
        workflow.logger.info(f"Starting simple workflow with data: {test_data}")
        
        # Import activities inside workflow
        with workflow.unsafe.imports_passed_through():
            from activities import (
                send_notification,
                generate_llm_content,
            )
        
        # Step 1: Generate some content
        try:
            content_result = await workflow.execute_activity(
                generate_llm_content,
                args=[{
                    "prompt": "Generate a brief test message",
                    "context": test_data
                }],
                start_to_close_timeout=timedelta(minutes=2),
            )
            self.results["content_generation"] = content_result
            workflow.logger.info(f"Content generated: {content_result}")
        except Exception as e:
            workflow.logger.error(f"Content generation failed: {e}")
            self.results["content_generation"] = {"error": str(e)}
        
        # Step 2: Send notification
        try:
            notification_result = await workflow.execute_activity(
                send_notification,
                args=[{
                    "recipient": "test@example.com",
                    "subject": "Test Workflow Completed",
                    "body": f"Workflow completed successfully. Test ID: {test_data.get('test_id')}"
                }],
                start_to_close_timeout=timedelta(minutes=1),
            )
            self.results["notification"] = notification_result
            workflow.logger.info(f"Notification sent: {notification_result}")
        except Exception as e:
            workflow.logger.error(f"Notification failed: {e}")
            self.results["notification"] = {"error": str(e)}
        
        return {
            "status": "completed",
            "test_id": test_data.get("test_id"),
            "results": self.results
        }


async def main():
    """Run the simple workflow example."""
    
    print("\n" + "="*70)
    print("SIMPLE WORKFLOW TEST (No Database Required)")
    print("="*70)
    
    # Connect to Temporal
    print("\n🔌 Connecting to Temporal...")
    client = await Client.connect("localhost:7233", namespace="default")
    print("✅ Connected to Temporal")
    
    # Test data
    test_id = str(uuid.uuid4())[:8]
    test_data = {
        "test_id": test_id,
        "message": "This is a simple test workflow"
    }
    
    print(f"\n📋 Test ID: {test_id}")
    print(f"📊 Test Data: {test_data}")
    
    # Start workflow
    print("\n🚀 Starting workflow...")
    workflow_id = f"simple-test-{test_id}"
    
    handle = await client.start_workflow(
        SimpleTestWorkflow.run,
        args=[test_data],
        id=workflow_id,
        task_queue="mudda-ai-workflows",
    )
    
    print(f"✅ Workflow started: {workflow_id}")
    print(f"🔗 View in UI: http://localhost:8233/namespaces/default/workflows/{workflow_id}")
    
    # Wait for result
    print("\n⏳ Waiting for completion...")
    try:
        result = await handle.result()
        
        print("\n" + "="*70)
        print("✅ WORKFLOW COMPLETED")
        print("="*70)
        print(f"\nStatus: {result.get('status')}")
        print(f"Test ID: {result.get('test_id')}")
        print(f"\nResults:")
        for key, value in result.get('results', {}).items():
            print(f"  • {key}: {value}")
        
        print("\n" + "="*70)
        print("🎉 Test completed successfully!")
        print("="*70)
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ WORKFLOW FAILED")
        print("="*70)
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("  1. Is the worker running? Run: python temporal_worker.py")
        print("  2. Check worker logs for activity errors")
        print("  3. View workflow in UI: http://localhost:8233")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
