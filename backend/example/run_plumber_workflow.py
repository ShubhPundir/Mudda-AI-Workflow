"""
Example workflow executor — demonstrates the worker dispatch workflow.

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
from example.example_workflow_plan import WORKER_DISPATCH_WORKFLOW_PLAN

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Run the worker dispatch workflow."""
    logger.info("=" * 80)
    logger.info("Starting Example Workflow: Worker Dispatch and Site Documentation")
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
                execution_data=WORKER_DISPATCH_WORKFLOW_PLAN,
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
        workflow_plan=WORKER_DISPATCH_WORKFLOW_PLAN,
        execution_id=str(execution_id)
    )
    logger.info(f"✓ Workflow started: {workflow_id}")

    # Step 4: Wait for completion and get results
    logger.info("\n[4/4] Waiting for workflow completion...")

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
                    if len(str(value)) > 100:
                        logger.info(f"  {key}: {str(value)[:100]}...")
                    else:
                        logger.info(f"  {key}: {value}")
            else:
                logger.info(f"  {step_result}")

        # Highlight key outputs
        dispatch_result = results.get('step_001_dispatch_worker', {})
        photos_result = results.get('step_002_request_photos', {})
        completion_result = results.get('step_003_confirm_completion', {})

        logger.info("\n" + "=" * 80)
        logger.info("KEY OUTPUTS")
        logger.info("=" * 80)

        if dispatch_result:
            logger.info(f"\n🛠️ Worker Dispatched:")
            logger.info(f"   Dispatch ID: {dispatch_result.get('dispatch_id')}")
            logger.info(f"   Status: {dispatch_result.get('status')}")
            logger.info(f"   Worker Notified: {dispatch_result.get('worker_notified')}")
            logger.info(f"   Message: {dispatch_result.get('message')}")

        if photos_result:
            logger.info(f"\n📷 Photos Requested:")
            logger.info(f"   Request ID: {photos_result.get('request_id')}")
            logger.info(f"   Status: {photos_result.get('status')}")

        if completion_result:
            logger.info(f"\n✅ Task Completed:")
            logger.info(f"   Status: {completion_result.get('status')}")
            logger.info(f"   Confirmed At: {completion_result.get('confirmed_at')}")

        logger.info("\n" + "=" * 80)

    except Exception as e:
        logger.error(f"\n❌ Workflow failed: {e}", exc_info=True)
        raise

    finally:
        await client_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
