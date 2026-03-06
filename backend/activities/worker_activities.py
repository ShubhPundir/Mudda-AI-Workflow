"""
Worker and dispatch-related activities.
"""
import logging
from datetime import datetime, timezone
import uuid
from termcolor import colored
from temporalio import activity
from schemas.activity_schemas import (
    DispatchWorkerInput,
    DispatchWorkerOutput,
    RequestSitePhotosInput,
    RequestSitePhotosOutput,
    ConfirmTaskCompletionInput,
    ConfirmTaskCompletionOutput,
)

logger = logging.getLogger(__name__)


@activity.defn
async def dispatch_worker_activity(inputs: DispatchWorkerInput) -> DispatchWorkerOutput:
    """
    Mock activity to dispatch a worker to a location.
    In a real system, this would call an external fleet management API.
    """
    step_id = inputs.step_id or "unknown"
    dispatch_id = f"disp_{uuid.uuid4().hex[:8]}"

    logger.info(
        colored(
            f"🛠️ [DISPATCH] Dispatching {inputs.worker_type} for '{inputs.issue_id}' at {inputs.location}",
            "yellow",
            attrs=["bold"],
        )
    )

    return DispatchWorkerOutput(
        step_id=step_id,
        status="dispatched",
        dispatch_id=dispatch_id,
        worker_notified=True,
        message=f"Dispatched {inputs.worker_type} with urgency: {inputs.urgency}",
    )


@activity.defn
async def request_site_photos_activity(
    inputs: RequestSitePhotosInput,
) -> RequestSitePhotosOutput:
    """
    Mock activity to request photos from a dispatched worker.
    """
    step_id = inputs.step_id or "unknown"
    request_id = f"req_{uuid.uuid4().hex[:8]}"

    logger.info(
        colored(
            f"📷 [PHOTOS REQUEST] Requesting photos for dispatch {inputs.dispatch_id}. Message: {inputs.message}",
            "cyan",
            attrs=["bold"],
        )
    )

    return RequestSitePhotosOutput(
        step_id=step_id, status="requested", request_id=request_id
    )


@activity.defn
async def confirm_task_completion_activity(
    inputs: ConfirmTaskCompletionInput,
) -> ConfirmTaskCompletionOutput:
    """
    Mock activity to finalize the completion of a dispatch task.
    """
    step_id = inputs.step_id or "unknown"

    logger.info(
        colored(
            f"✅ [COMPLETION] Confirming completion for dispatch {inputs.dispatch_id}.",
            "green",
            attrs=["bold"],
        )
    )

    timestamp = datetime.now(timezone.utc).isoformat()

    return ConfirmTaskCompletionOutput(
        step_id=step_id, status="completed", confirmed_at=timestamp
    )
