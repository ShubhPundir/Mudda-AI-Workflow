"""
Worker and dispatch-related activities.
Enhanced with realistic mock data for demo purposes.
"""
import logging
import asyncio
import random
from datetime import datetime, timezone, timedelta
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

# Mock worker database for realistic demo
# TODO: replace with results from CRM
MOCK_WORKERS = {
    "plumber": [
        {"name": "Rajesh Kumar", "phone": "+91-98765-43210", "rating": 4.8},
        {"name": "Amit Sharma", "phone": "+91-98765-43211", "rating": 4.6},
        {"name": "Vikram Singh", "phone": "+91-98765-43212", "rating": 4.9},
    ],
    "electrician": [
        {"name": "Suresh Patel", "phone": "+91-98765-43213", "rating": 4.7},
        {"name": "Ramesh Gupta", "phone": "+91-98765-43214", "rating": 4.5},
    ],
    "carpenter": [
        {"name": "Mohan Das", "phone": "+91-98765-43215", "rating": 4.6},
    ],
}

WORKER_RESPONSES = [
    "On my way! Will reach in 15 minutes.",
    "Acknowledged. Heading to the location now.",
    "Received the dispatch. ETA 20 minutes.",
    "Got it! I'm nearby, will be there shortly.",
]

MOCK_SITE_PHOTOS = [
    "https://mudda-field-photos.s3.ap-south-1.amazonaws.com/cleaning.png",
    "https://mudda-field-photos.s3.ap-south-1.amazonaws.com/broken-pipe.png",
    "https://mudda-field-photos.s3.ap-south-1.amazonaws.com/underground-pipeline.png",
    "https://mudda-field-photos.s3.ap-south-1.amazonaws.com/geyser.jpg",
    "https://mudda-field-photos.s3.ap-south-1.amazonaws.com/plumber.png",
]

PHOTO_NOTES = [
    "Uploaded before and after photos. The damage was worse than expected.",
    "Photos uploaded. Captured all angles of the repair work.",
    "Before/after photos attached. Also included close-ups of the fix.",
    "Photos uploaded showing the complete repair process.",
]

COMPLETION_NOTES = [
    "Job completed successfully. Tested everything thoroughly.",
    "Repair finished. All systems working normally now.",
    "Task completed. Customer satisfied with the work.",
    "Work done. No issues found during final inspection.",
]

MATERIALS_LIST = {
    "plumber": [
        ["PVC pipe (2m)", "Pipe fittings", "Teflon tape", "Pipe cement"],
        ["Copper pipe (1.5m)", "Solder", "Flux", "Pipe wrench"],
        ["Drain snake", "Pipe sealant", "Rubber gaskets"],
    ],
    "electrician": [
        ["Wire (10m)", "Circuit breaker", "Wire nuts", "Electrical tape"],
        ["Light fixtures", "Switches", "Junction box"],
    ],
    "carpenter": [
        ["Wood planks", "Screws", "Wood glue", "Sandpaper"],
        ["Hinges", "Door handle", "Wood filler"],
    ],
}


@activity.defn
async def dispatch_worker_activity(inputs: DispatchWorkerInput) -> DispatchWorkerOutput:
    """
    Mock activity to dispatch a worker to a location.
    Simulates realistic bi-directional communication with field workers.
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

    # Simulate API call delay
    await asyncio.sleep(1.5)

    # Select a worker from the mock database
    workers = MOCK_WORKERS.get(inputs.worker_type, MOCK_WORKERS["plumber"])
    selected_worker = random.choice(workers)

    # Calculate estimated arrival based on urgency
    if inputs.urgency == "critical":
        eta_minutes = random.randint(10, 20)
    elif inputs.urgency == "high":
        eta_minutes = random.randint(20, 40)
    else:
        eta_minutes = random.randint(40, 90)

    estimated_arrival = (datetime.now(timezone.utc) + timedelta(minutes=eta_minutes)).strftime("%I:%M %p")
    worker_response = random.choice(WORKER_RESPONSES)

    logger.info(
        colored(
            f"   ✓ Worker assigned: {selected_worker['name']} (Rating: {selected_worker['rating']}⭐)",
            "green",
        )
    )
    logger.info(
        colored(
            f"   📱 Worker response: \"{worker_response}\"",
            "cyan",
        )
    )
    logger.info(
        colored(
            f"   🕐 ETA: {estimated_arrival} ({eta_minutes} minutes)",
            "blue",
        )
    )

    return DispatchWorkerOutput(
        step_id=step_id,
        status="dispatched",
        dispatch_id=dispatch_id,
        worker_notified=True,
        message=f"Dispatched {inputs.worker_type} with urgency: {inputs.urgency}",
        worker_name=selected_worker["name"],
        worker_phone=selected_worker["phone"],
        estimated_arrival=estimated_arrival,
        worker_response=worker_response,
    )


@activity.defn
async def request_site_photos_activity(
    inputs: RequestSitePhotosInput,
) -> RequestSitePhotosOutput:
    """
    Mock activity to request photos from a dispatched worker.
    Simulates worker uploading photos with realistic delays.
    """
    step_id = inputs.step_id or "unknown"
    request_id = f"req_{uuid.uuid4().hex[:8]}"

    logger.info(
        colored(
            f"📷 [PHOTOS REQUEST] Requesting photos for dispatch {inputs.dispatch_id}",
            "cyan",
            attrs=["bold"],
        )
    )
    logger.info(
        colored(
            f"   Message to worker: \"{inputs.message}\"",
            "white",
        )
    )

    # Simulate time for worker to take and upload photos
    await asyncio.sleep(2)

    # Generate mock photo data
    num_photos = random.randint(1, 3)
    photo_urls = random.sample(MOCK_SITE_PHOTOS, num_photos)
    worker_notes = random.choice(PHOTO_NOTES)

    logger.info(
        colored(
            f"   ✓ Worker uploaded {num_photos} photos",
            "green",
        )
    )
    logger.info(
        colored(
            f"   💬 Worker notes: \"{worker_notes}\"",
            "cyan",
        )
    )

    for i, url in enumerate(photo_urls, 1):
        logger.info(
            colored(
                f"      📸 Photo {i}: {url}",
                "white",
            )
        )

    return RequestSitePhotosOutput(
        step_id=step_id,
        status="photos_received",
        request_id=request_id,
        photos_uploaded=num_photos,
        photo_urls=photo_urls,
        worker_notes=worker_notes,
    )


@activity.defn
async def confirm_task_completion_activity(
    inputs: ConfirmTaskCompletionInput,
) -> ConfirmTaskCompletionOutput:
    """
    Mock activity to finalize the completion of a dispatch task.
    Simulates worker submitting completion report with details.
    """
    step_id = inputs.step_id or "unknown"

    logger.info(
        colored(
            f"✅ [COMPLETION] Confirming completion for dispatch {inputs.dispatch_id}",
            "green",
            attrs=["bold"],
        )
    )

    # Simulate processing delay
    await asyncio.sleep(1)

    timestamp = datetime.now(timezone.utc).isoformat()
    completion_notes = random.choice(COMPLETION_NOTES)
    time_spent = random.randint(45, 180)  # 45 minutes to 3 hours
    
    # Determine materials based on worker type (extract from dispatch_id context)
    # For demo, randomly pick plumber materials
    materials = random.choice(MATERIALS_LIST.get("plumber", [["Generic materials"]]))
    
    follow_up = random.choice([True, False])

    logger.info(
        colored(
            f"   ✓ Task marked as completed",
            "green",
        )
    )
    logger.info(
        colored(
            f"   ⏱️  Time spent: {time_spent} minutes ({time_spent // 60}h {time_spent % 60}m)",
            "blue",
        )
    )
    logger.info(
        colored(
            f"   💬 Completion notes: \"{completion_notes}\"",
            "cyan",
        )
    )
    logger.info(
        colored(
            f"   🔧 Materials used: {', '.join(materials)}",
            "yellow",
        )
    )
    logger.info(
        colored(
            f"   🔄 Follow-up required: {'Yes' if follow_up else 'No'}",
            "magenta",
        )
    )

    return ConfirmTaskCompletionOutput(
        step_id=step_id,
        status="completed",
        confirmed_at=timestamp,
        completion_notes=completion_notes,
        time_spent_minutes=time_spent,
        materials_used=materials,
        follow_up_required=follow_up,
    )
