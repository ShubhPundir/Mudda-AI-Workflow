"""
Example Workflow Runner for Local Temporal Development

This script demonstrates how to:
1. Connect to local Temporal (temporal dev)
2. Create a workflow plan using activities from registry.py
3. Execute the workflow
4. Query workflow status
5. Send approval signals for human-in-the-loop steps

Prerequisites:
    - Temporal dev server running: `temporal server start-dev`
    - Worker running: `python backend/temporal_worker.py`
    - Database configured with proper tables

Usage:
    cd backend
    python example/example_workflow_runner.py
"""
import asyncio
import logging
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Add backend directory to Python path if running from project root
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from temporal.client import temporal_client_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_example_workflow_plan() -> Dict[str, Any]:
    """
    Create a sample workflow plan that demonstrates various activities.
    
    This workflow simulates a plumber dispatch scenario:
    1. Fetch issue details
    2. Generate dispatch text using LLM
    3. Request human approval
    4. Contact plumber
    5. Generate PDF report
    6. Send notification
    7. Update issue status
    """
    return {
        "workflow_name": "Example Plumber Dispatch Workflow",
        "description": "Demonstrates activity execution with human approval",
        "steps": [
            {
                "step_id": "step_1_fetch_issue",
                "activity_id": "fetch_issue_details_activity",
                "description": "Fetch issue details from database",
                "inputs": {
                    "issue_id": "ISSUE-001"
                },
                "requires_approval": False
            },
            {
                "step_id": "step_2_generate_dispatch",
                "activity_id": "llm_generate_dispatch_text_activity",
                "description": "Generate dispatch instructions using AI",
                "inputs": {
                    "issue_details": "{{step_1_fetch_issue.issue_details}}"
                },
                "requires_approval": False
            },
            {
                "step_id": "step_3_human_approval",
                "activity_id": "human_feedback_activity",
                "description": "Request approval from supervisor",
                "inputs": {
                    "message": "Please review the dispatch plan",
                    "options": ["approve", "reject", "modify"]
                },
                "requires_approval": True  # This step requires signal approval
            },
            {
                "step_id": "step_4_contact_plumber",
                "activity_id": "contact_plumber",
                "description": "Contact plumber dispatch system",
                "inputs": {
                    "issue_id": "ISSUE-001",
                    "dispatch_text": "{{step_2_generate_dispatch.dispatch_text}}"
                },
                "requires_approval": False
            },
            {
                "step_id": "step_5_generate_report",
                "activity_id": "pdf_service_activity",
                "description": "Generate PDF report",
                "inputs": {
                    "content": "{{step_2_generate_dispatch.dispatch_text}}",
                    "template_id": "dispatch_report"
                },
                "requires_approval": False
            },
            {
                "step_id": "step_6_send_notification",
                "activity_id": "send_notification",
                "description": "Send email notification",
                "inputs": {
                    "recipient": "supervisor@example.com",
                    "subject": "Plumber Dispatch Completed",
                    "body": "Dispatch completed. Report: {{step_5_generate_report.report_url}}"
                },
                "requires_approval": False
            },
            {
                "step_id": "step_7_update_issue",
                "activity_id": "update_issue_activity",
                "description": "Update issue status in database",
                "inputs": {
                    "issue_id": "ISSUE-001",
                    "status": "dispatched",
                    "notes": "Plumber contacted. Booking ID: {{step_4_contact_plumber.booking_id}}"
                },
                "requires_approval": False
            }
        ]
    }


def create_simple_workflow_plan() -> Dict[str, Any]:
    """
    Create a minimal workflow for quick testing.
    """
    return {
        "workflow_name": "Simple Test Workflow",
        "description": "Minimal workflow for testing",
        "steps": [
            {
                "step_id": "step_1_fetch",
                "activity_id": "fetch_issue_details_activity",
                "description": "Fetch issue details",
                "inputs": {
                    "issue_id": "TEST-001"
                },
                "requires_approval": False
            },
            {
                "step_id": "step_2_notify",
                "activity_id": "send_notification",
                "description": "Send notification",
                "inputs": {
                    "recipient": "test@example.com",
                    "subject": "Test Notification",
                    "body": "This is a test notification"
                },
                "requires_approval": False
            }
        ]
    }


async def run_workflow_example():
    """
    Main example: execute a workflow and monitor its progress.
    """
    logger.info("=" * 60)
    logger.info("Starting Example Workflow Runner")
    logger.info("=" * 60)
    
    # Connect to Temporal
    await temporal_client_manager.connect()
    logger.info("✓ Connected to Temporal")
    
    # Create workflow plan (choose one)
    workflow_plan = create_simple_workflow_plan()
    # workflow_plan = create_example_workflow_plan()  # Use this for full example
    
    # Generate proper UUID for execution ID (required by database)
    execution_id = str(uuid.uuid4())
    
    logger.info(f"Workflow Plan: {workflow_plan['workflow_name']}")
    logger.info(f"Execution ID: {execution_id}")
    logger.info(f"Steps: {len(workflow_plan['steps'])}")
    
    # Start workflow execution
    logger.info("\n" + "=" * 60)
    logger.info("Starting workflow execution...")
    logger.info("=" * 60)
    
    workflow_id = await temporal_client_manager.execute_workflow(
        workflow_plan=workflow_plan,
        execution_id=execution_id
    )
    
    logger.info(f"✓ Workflow started with ID: {workflow_id}")
    
    # Monitor workflow progress
    logger.info("\n" + "=" * 60)
    logger.info("Monitoring workflow progress...")
    logger.info("=" * 60)
    
    # Query status periodically
    for i in range(5):
        await asyncio.sleep(2)
        try:
            status = await temporal_client_manager.query_workflow_status(workflow_id)
            logger.info(f"\nStatus check #{i+1}:")
            logger.info(f"  Completed steps: {len(status.get('execution_results', {}))}")
            logger.info(f"  Approved steps: {list(status.get('approved_steps', {}).keys())}")
            
            # Check if any step requires approval
            if workflow_plan['workflow_name'] == "Example Plumber Dispatch Workflow":
                # Send approval signal for step_3 if needed
                if 'step_3_human_approval' not in status.get('approved_steps', {}):
                    logger.info("\n⚠ Step requires approval. Sending approval signal...")
                    await temporal_client_manager.signal_approval(
                        workflow_id=workflow_id,
                        step_id="step_3_human_approval"
                    )
                    logger.info("✓ Approval signal sent")
        except Exception as e:
            logger.warning(f"Status query failed: {e}")
    
    # Wait for final result
    logger.info("\n" + "=" * 60)
    logger.info("Waiting for workflow completion...")
    logger.info("=" * 60)
    
    try:
        result = await temporal_client_manager.get_workflow_result(workflow_id)
        
        logger.info("\n" + "=" * 60)
        logger.info("WORKFLOW COMPLETED")
        logger.info("=" * 60)
        logger.info(f"Status: {result.get('status')}")
        logger.info(f"Workflow: {result.get('workflow_name')}")
        logger.info(f"\nResults:")
        for step_id, step_result in result.get('results', {}).items():
            logger.info(f"  {step_id}: {step_result}")
        
        if result.get('ai_context'):
            logger.info(f"\nAI Context: {result.get('ai_context')}")
            
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        raise


async def main():
    """Entry point."""
    try:
        await run_workflow_example()
    except KeyboardInterrupt:
        logger.info("\n\nInterrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        await temporal_client_manager.close()
        logger.info("\n✓ Disconnected from Temporal")


if __name__ == "__main__":
    asyncio.run(main())
