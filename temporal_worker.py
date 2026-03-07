"""
Temporal worker entry point for Mudda AI Workflow system.

Starts the Temporal worker using the new modular architecture.
Run this file directly:  python temporal_worker.py
"""
import asyncio
import logging
import os
import sys

# Ensure the backend directory is on the Python path so that
# relative package imports (activities, workflows, etc.) resolve.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from temporal.worker import TemporalWorkerManager

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Start the Temporal worker."""
    temporal_host = os.getenv("TEMPORAL_HOST", "localhost:7233")
    temporal_namespace = os.getenv("TEMPORAL_NAMESPACE", "default")

    logger.info("=" * 60)
    logger.info("Starting Mudda AI Temporal Worker")
    logger.info("=" * 60)
    logger.info("Temporal Host:      %s", temporal_host)
    logger.info("Temporal Namespace: %s", temporal_namespace)
    logger.info("Task Queue:         mudda-ai-workflows")
    logger.info("-" * 60)

    worker_manager = TemporalWorkerManager()

    try:
        await worker_manager.start()
    except KeyboardInterrupt:
        logger.info("Worker stopped by user (KeyboardInterrupt)")
    except Exception as exc:
        logger.error("Worker error: %s", exc, exc_info=True)
        raise
    finally:
        await worker_manager.shutdown()
        logger.info("Worker shut down cleanly")


if __name__ == "__main__":
    asyncio.run(main())
