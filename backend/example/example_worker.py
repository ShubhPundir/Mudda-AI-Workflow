"""
Example Temporal worker — starts a worker to process the example workflow.

This worker uses the same TemporalWorkerManager as production, ensuring
the example workflow runs exactly as a real workflow would.

Usage:
    python -m example.example_worker

Keep this running in one terminal while executing run_example_workflow.py in another.
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from temporal.worker import TemporalWorkerManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Start the Temporal worker."""
    logger.info("=" * 80)
    logger.info("Starting Example Temporal Worker")
    logger.info("=" * 80)
    logger.info("\nThis worker will process workflows on the 'mudda-ai-workflows' queue")
    logger.info("Press Ctrl+C to stop\n")
    
    manager = TemporalWorkerManager()
    
    try:
        await manager.start()
    except KeyboardInterrupt:
        logger.info("\n\nShutting down worker...")
        await manager.shutdown()
        logger.info("Worker stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nExiting...")
