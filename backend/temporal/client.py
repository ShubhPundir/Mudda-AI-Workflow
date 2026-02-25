"""
Temporal client manager — single-client instance with clean lifecycle.

Handles connection, workflow execution, signalling, and result retrieval.
Separated from the worker so the FastAPI app can use the client
without starting a worker in the same process.
"""
import logging
import os
from typing import Any, Dict, Optional

from temporalio.client import Client

logger = logging.getLogger(__name__)

# Default task queue shared across the system
TASK_QUEUE = "mudda-ai-workflows"


class TemporalClientManager:
    """
    Manages a singleton Temporal client connection.

    Usage:
        manager = TemporalClientManager()
        await manager.connect()
        wf_id = await manager.execute_workflow(plan, exec_id)
        result = await manager.get_workflow_result(wf_id)
    """

    def __init__(self) -> None:
        self._client: Optional[Client] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    async def connect(self) -> Client:
        """
        Connect to the Temporal server (idempotent).

        Returns:
            The connected Temporal Client.
        """
        if self._client is not None:
            return self._client

        host = os.getenv("TEMPORAL_HOST", "localhost:7233")
        namespace = os.getenv("TEMPORAL_NAMESPACE", "default")

        logger.info("Connecting to Temporal — host=%s namespace=%s", host, namespace)
        self._client = await Client.connect(host, namespace=namespace)
        logger.info("Temporal client connected")

        return self._client

    @property
    def client(self) -> Client:
        """Return the connected client or raise if not connected."""
        if self._client is None:
            raise RuntimeError(
                "Temporal client not connected. Call await manager.connect() first."
            )
        return self._client

    async def close(self) -> None:
        """Shut down the Temporal client gracefully."""
        if self._client is not None:
            logger.info("Closing Temporal client connection")
            # temporalio.Client currently has no explicit close, but we
            # reset the reference for good hygiene.
            self._client = None

    # ------------------------------------------------------------------
    # Workflow operations
    # ------------------------------------------------------------------
    async def execute_workflow(
        self,
        workflow_plan: Dict[str, Any],
        execution_id: str,
    ) -> str:
        """
        Start execution of a workflow plan.

        Args:
            workflow_plan: The workflow plan dict (must contain 'steps').
            execution_id: ID of the WorkflowExecution DB record.

        Returns:
            Temporal workflow ID string.
        """
        await self.connect()

        # Lazy import to avoid circular imports at module level
        from workflows.mudda_workflow import MuddaWorkflow

        handle = await self.client.start_workflow(
            MuddaWorkflow.run,
            args=[workflow_plan, execution_id],
            id=f"mudda-workflow-{execution_id}",
            task_queue=TASK_QUEUE,
        )

        logger.info(
            "Workflow started — temporal_id=%s execution_id=%s",
            handle.id,
            execution_id,
        )
        return handle.id

    async def signal_approval(self, workflow_id: str, step_id: str) -> None:
        """
        Send an approval signal to a running workflow.

        Args:
            workflow_id: Temporal workflow ID.
            step_id: ID of the step to approve.
        """
        await self.connect()

        from workflows.mudda_workflow import MuddaWorkflow

        handle = self.client.get_workflow_handle(workflow_id)
        await handle.signal(MuddaWorkflow.approve_step, step_id)

        logger.info(
            "Approval signal sent — workflow_id=%s step_id=%s",
            workflow_id,
            step_id,
        )

    async def get_workflow_result(self, workflow_id: str) -> Dict[str, Any]:
        """
        Wait for and return the result of a workflow execution.

        Args:
            workflow_id: Temporal workflow ID.

        Returns:
            Workflow execution result dict.
        """
        await self.connect()

        handle = self.client.get_workflow_handle(workflow_id)
        result = await handle.result()

        logger.info("Workflow result retrieved — workflow_id=%s", workflow_id)
        return result

    async def query_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Query the current state of a running workflow (non-blocking).

        Args:
            workflow_id: Temporal workflow ID.

        Returns:
            Current workflow state dict.
        """
        await self.connect()

        from workflows.mudda_workflow import MuddaWorkflow

        handle = self.client.get_workflow_handle(workflow_id)
        status = await handle.query(MuddaWorkflow.get_status)

        return status


# ---------------------------------------------------------------------------
# Global singleton instance
# ---------------------------------------------------------------------------
temporal_client_manager = TemporalClientManager()
