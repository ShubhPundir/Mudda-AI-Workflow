"""
Example workflow executor — demonstrates the plumber dispatch + reporting workflow.

This script:
1. Connects to the local Temporal server
2. Creates a WorkflowExecution record in the database
3. Starts the workflow using TemporalClientManager
4. Waits for completion and prints results

Usage:
    python -m example.run_plumber_workflow
"""
import asyncio
import logging
import sys
from pathlib import Path
from uuid import uuid4

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from temporal.client import TemporalClientManager
from sessions.database import AsyncSessionLocal
from models.workflow_execution import WorkflowExecution
from example.example_plumber_workflow_plan import PLUMBER_WORKFLOW_PLAN

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Run the plumber dispatch workflow."""
    logger.info("=" * 80)
    logger.info("Starting Example Workflow: Emergency Plumber Dispatch and Reporting")
    logger.info("=" * 80)

    # Step 0: Ensure database schema exists
    logger.info("\n[0/4] Initializing database schema...")
    try:
        from sessions.database import engine
        from models.base import Base
        from sqlalchemy import text

        async with engine.begin() as conn:
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS workflow"))
            await conn.run_sync(Base.metadata.create_all)

        logger.info("✓ Database schema initialized")
    except Exception as e:
        logger.warning(f"Database initialization warning (may already exist): {e}")

    # Step 1: Create a WorkflowExecution record in the database
    logger.info("\n[1/4] Creating WorkflowExecution record in database...")

    execution_id = uuid4()
    workflow_plan_id = uuid4()

    async with AsyncSessionLocal() as db:
        try:
            execution = WorkflowExecution(
                id=execution_id,
                workflow_plan_id=workflow_plan_id,
                execution_data=PLUMBER_WORKFLOW_PLAN,
                status="pending"
            )
            db.add(execution)
            await db.commit()
            await db.refresh(execution)

            logger.info(f"✓ Created execution record: {execution_id}")
        except Exception as e:
            logger.error(f"Failed to create execution record: {e}")
            await db.rollback()
            raise

    # Step 2: Connect to Temporal
    logger.info("\n[2/4] Connecting to Temporal server...")
    client_manager = TemporalClientManager()
    await client_manager.connect()
    logger.info("✓ Connected to Temporal")

    # Step 3: Start the workflow
    logger.info("\n[3/4] Starting workflow execution...")
    workflow_id = await client_manager.execute_workflow(
        workflow_plan=PLUMBER_WORKFLOW_PLAN,
        execution_id=str(execution_id)
    )
    logger.info(f"✓ Workflow started: {workflow_id}")

    # Step 4: Wait for completion and get results
    logger.info("\n[4/4] Waiting for workflow completion...")
    logger.info("(This may take a few minutes depending on LLM and PDF generation)")

    try:
        result = await client_manager.get_workflow_result(workflow_id)

        logger.info("\n" + "=" * 80)
        logger.info("WORKFLOW COMPLETED SUCCESSFULLY!")
        logger.info("=" * 80)
        logger.info(f"\nWorkflow Status: {result.get('status')}")
        logger.info(f"Workflow Name: {result.get('workflow_name')}")

        # Display step results
        results = result.get('results', {})
        logger.info("\n--- Step Results ---")

        for step_id, step_result in results.items():
            logger.info(f"\n{step_id}:")
            if isinstance(step_result, dict):
                for key, value in step_result.items():
                    if key == 'ai_metadata':
                        logger.info(f"  {key}: {value}")
                    elif key == 'chat_transcript':
                        logger.info(f"  {key}: [{len(value)} messages]")
                    elif len(str(value)) > 100:
                        logger.info(f"  {key}: {str(value)[:100]}...")
                    else:
                        logger.info(f"  {key}: {value}")
            else:
                logger.info(f"  {step_result}")

        # Highlight key outputs
        plumber_result = results.get('step_001_contact_plumber', {})
        report_result = results.get('step_002_generate_report', {})
        email_result = results.get('step_003_send_notification', {})

        logger.info("\n" + "=" * 80)
        logger.info("KEY OUTPUTS")
        logger.info("=" * 80)

        if plumber_result:
            result_data = plumber_result.get('result', {})
            logger.info(f"\n💬 Plumber Chat Session:")
            logger.info(f"   Session ID: {result_data.get('session_id')}")
            logger.info(f"   Status: {result_data.get('session_status')}")
            logger.info(f"   Total Messages: {result_data.get('total_messages')}")
            logger.info(f"   Plumber ETA: {result_data.get('plumber_eta')}")
            logger.info(f"   Repair Duration: {result_data.get('repair_duration')}")
            logger.info(f"   Repair Status: {result_data.get('repair_status')}")
            logger.info(f"   Pressure Test: {result_data.get('pressure_test')}")

            # Print chat transcript
            transcript = result_data.get('chat_transcript', [])
            if transcript:
                logger.info(f"\n   --- Chat Transcript ({len(transcript)} messages) ---")
                for msg in transcript:
                    role = msg.get('role', '?').upper()
                    icon = "🤖" if role == "SYSTEM" else "🔧"
                    text = msg.get('message', '')
                    ts = msg.get('timestamp', '')
                    if len(text) > 100:
                        text = text[:100] + "..."
                    logger.info(f"   {icon} [{role}] {ts}: {text}")

        if report_result:
            logger.info(f"\n📄 Field Report Generated:")
            logger.info(f"   File: {report_result.get('file_path')}")
            logger.info(f"   S3 URL: {report_result.get('s3_url')}")
            logger.info(f"   Size: {report_result.get('size_bytes')} bytes")

        if email_result:
            logger.info(f"\n📧 Notification Sent:")
            logger.info(f"   To: {email_result.get('to')}")
            logger.info(f"   Subject: {email_result.get('subject')}")
            logger.info(f"   Message ID: {email_result.get('message_id')}")

        logger.info("\n" + "=" * 80)

    except Exception as e:
        logger.error(f"\n❌ Workflow failed: {e}", exc_info=True)
        raise

    finally:
        await client_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
