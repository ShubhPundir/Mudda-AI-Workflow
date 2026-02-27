"""
Temporal worker manager — registers workflows and individual activity functions.

Activities are registered as callables (NOT classes), which is the
correct pattern for temporalio-python.
"""
import logging
import os
from typing import Optional

from temporalio.client import Client
from temporalio.worker import Worker

logger = logging.getLogger(__name__)

# Default task queue shared across the system
TASK_QUEUE = "mudda-ai-workflows"


class TemporalWorkerManager:
    """
    Manages the Temporal worker lifecycle.

    Registers:
        - MuddaWorkflow (workflow class)
        - All activity *functions* from the activities package

    Usage:
        manager = TemporalWorkerManager()
        await manager.start()   # blocks until worker is shut down
    """

    def __init__(self) -> None:
        self._client: Optional[Client] = None
        self._worker: Optional[Worker] = None

    async def _connect(self) -> Client:
        """Connect to the Temporal server (idempotent)."""
        if self._client is not None:
            return self._client

        host = os.getenv("TEMPORAL_HOST", "localhost:7233")
        namespace = os.getenv("TEMPORAL_NAMESPACE", "default")

        logger.info("Worker connecting to Temporal — host=%s namespace=%s", host, namespace)
        self._client = await Client.connect(host, namespace=namespace)
        return self._client

    def _create_worker(self, client: Client) -> Worker:
        """
        Create the Temporal worker with all workflows and activities registered.

        Activities are registered as individual async functions — NOT as a class.
        """
        from workflows.mudda_workflow import MuddaWorkflow
        import activities

        # Collect all activities registered in activities/__init__.py
        all_activities = [
            getattr(activities, name) 
            for name in activities.__all__
        ]

        worker = Worker(
            client,
            task_queue=TASK_QUEUE,
            workflows=[MuddaWorkflow],
            activities=all_activities,
        )

        logger.info(
            "Worker created — task_queue=%s workflows=[MuddaWorkflow] "
            "activities=%s",
            TASK_QUEUE,
            activities.__all__,
        )
        return worker

    async def start(self) -> None:
        """
        Start the Temporal worker (blocking).

        This method connects to the Temporal server, creates the worker,
        and runs it. It blocks until the worker is shut down (e.g., via
        KeyboardInterrupt or cancellation).
        """
        client = await self._connect()
        self._worker = self._create_worker(client)

        logger.info("Starting Temporal worker on queue '%s'…", TASK_QUEUE)
        await self._worker.run()

    async def shutdown(self) -> None:
        """Gracefully shut down the worker."""
        if self._worker is not None:
            logger.info("Shutting down Temporal worker")
            # Worker.run() handles its own shutdown when the task is cancelled.
            self._worker = None
        self._client = None
