"""
Example workflow executor — demonstrates how to run a workflow using the Temporal client.

This script:
1. Connects to the local Temporal server
2. Creates a WorkflowExecution record in the database
3. Starts the workflow using TemporalClientManager
4. Waits for completion and prints results

Usage:
    python -m example.run_example_workflow
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
from example.example_workflow_plan import PHOTOSYNTHESIS_WORKFLOW_PLAN

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Run the example workflow."""
    logger.info("=" * 80)
    logger.info("Starting Example Workflow: Photosynthesis Document Generation")
    logger.info("=" * 80)
    
    # Step 0: Ensure database schema exists
    logger.info("\n[0/4] Initializing database schema...")
    try:
        from sessions.database import engine
        from models.base import Base
        from sqlalchemy import text
        
        async with engine.begin() as conn:
            # Create schema if it doesn't exist
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS workflow"))
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✓ Database schema initialized")
    except Exception as e:
        logger.warning(f"Database initialization warning (may already exist): {e}")
    
    # Step 1: Create a WorkflowExecution record in the database
    logger.info("\n[1/4] Creating WorkflowExecution record in database...")
    
    # Generate UUIDs for the execution
    execution_id = uuid4()
    workflow_plan_id = uuid4()
    
    async with AsyncSessionLocal() as db:
        try:
            execution = WorkflowExecution(
                id=execution_id,
                workflow_plan_id=workflow_plan_id,
                execution_data=PHOTOSYNTHESIS_WORKFLOW_PLAN,
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
        workflow_plan=PHOTOSYNTHESIS_WORKFLOW_PLAN,
        execution_id=str(execution_id)  # Convert UUID to string for Temporal
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
                    elif len(str(value)) > 100:
                        logger.info(f"  {key}: {str(value)[:100]}...")
                    else:
                        logger.info(f"  {key}: {value}")
            else:
                logger.info(f"  {step_result}")
        
        # Highlight the PDF and email results
        pdf_result = results.get('step_001_generate_pdf', {})
        email_result = results.get('step_002_send_email', {})
        
        logger.info("\n" + "=" * 80)
        logger.info("KEY OUTPUTS")
        logger.info("=" * 80)
        
        if pdf_result:
            logger.info(f"\n📄 PDF Generated:")
            logger.info(f"   File: {pdf_result.get('file_path')}")
            logger.info(f"   S3 URL: {pdf_result.get('s3_url')}")
            logger.info(f"   Size: {pdf_result.get('size_bytes')} bytes")
        
        if email_result:
            logger.info(f"\n📧 Email Sent:")
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
