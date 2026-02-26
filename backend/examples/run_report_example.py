import asyncio
import logging
import os
import sys
from datetime import timedelta

# Ensure the backend directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from temporalio.client import Client
from temporalio.worker import Worker
from dotenv import load_dotenv

# Import our workflow and activities
from examples.example_report_workflow import ExampleReportWorkflow
from activities.document_activities import generate_report
from activities.notification_activities import send_notification

# Load environment variables
load_dotenv()

async def main():
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ExampleRunner")

    # Connect to Temporal
    temporal_host = os.getenv("TEMPORAL_HOST", "localhost:7233")
    temporal_namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
    
    logger.info("Connecting to Temporal at %s (namespace: %s)...", temporal_host, temporal_namespace)
    try:
        client = await Client.connect(temporal_host, namespace=temporal_namespace)
    except Exception as e:
        logger.error("Failed to connect to Temporal. Is the server running? Error: %s", e)
        return

    # Task queue for this example
    task_queue = "example-report-task-queue"

    # Start Worker in the background
    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[ExampleReportWorkflow],
        activities=[generate_report, send_notification],
    )

    async with worker:
        logger.info("Worker started. Triggering ExampleReportWorkflow...")

        # Workflow Input
        # Prompt: "Define Photosynthesis"
        workflow_input = {
            "problem_statement": "Define Photosynthesis",
            "title": "Educational Report: Photosynthesis",
            "report_type": "detailed",
            "email_to": "project.mudda@gmail.com",
            "step_id": "example-step-001"
        }

        # Execute Workflow
        workflow_id = f"report-wf-{int(asyncio.get_event_loop().time())}"
        try:
            result = await client.execute_workflow(
                ExampleReportWorkflow.run,
                workflow_input,
                id=workflow_id,
                task_queue=task_queue,
                execution_timeout=timedelta(minutes=10),
            )

            logger.info("Workflow completed successfully!")
            logger.info("Report File: %s", result["report"]["file_path"])
            logger.info("Email Message ID: %s", result["email"]["message_id"])
            logger.info("Result status: %s", result["status"])
            
            print("\n" + "="*50)
            print("🚀 WORKFLOW SUCCESSFUL!")
            print(f"Topic: {workflow_input['problem_statement']}")
            print(f"PDF Generated: {result['report']['file_path']}")
            print(f"Email Sent To: {workflow_input['email_to']}")
            print("="*50 + "\n")

        except Exception as e:
            logger.error("Workflow failed: %s", e)

if __name__ == "__main__":
    asyncio.run(main())
