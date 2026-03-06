"""
External service activities — DEMO MOCK.

Mocks the plumber dispatch as a bi-directional chat session.
The contact_plumber activity simulates opening a persistent channel,
exchanging messages between the system and the plumber, and returning
a full chat transcript.

Uses LLM to generate the initial dispatch instructions.
"""
import asyncio
import logging
from datetime import datetime, timedelta, timezone

from temporalio import activity

from infrastructure.plumber.plumber_factory import PlumberFactory
from sessions.llm import LLMFactory
from schemas.activity_schemas import (
    ContactPlumberInput,
    ContactPlumberOutput,
)

logger = logging.getLogger(__name__)

# Module-level adapter instances
_plumber_service = PlumberFactory.get_plumber_service()
_llm_service = LLMFactory.get_llm_service()

# ---------------------------------------------------------------------------
# Mock plumber responses for the bi-directional chat demo
# ---------------------------------------------------------------------------
_MOCK_PLUMBER_REPLIES = [
    {
        "delay_seconds": 1,
        "message": "Acknowledged. Reviewing the dispatch details now.",
    },
    {
        "delay_seconds": 2,
        "message": (
            "I can see the issue — burst pipe in the basement parking area. "
            "I'll bring the pipe repair kit and welding equipment. "
            "ETA: approximately 30 minutes."
        ),
    },
    {
        "delay_seconds": 1,
        "message": (
            "Arrived on site. Starting inspection of the burst pipe. "
            "Will send status updates as I work."
        ),
    },
    {
        "delay_seconds": 2,
        "message": (
            "Inspection complete — 6-inch PVC main has a 3-inch longitudinal crack. "
            "Shutting off the isolation valve and preparing a coupling repair. "
            "Estimated repair time: 45 minutes."
        ),
    },
    {
        "delay_seconds": 2,
        "message": (
            "Repair finished. Water flow restored and pressure tested at 60 PSI — "
            "holding steady. No further leaks detected. Cleaning up the area now."
        ),
    },
]


def _ts(base: datetime, offset_seconds: int) -> str:
    """Return an ISO-8601 timestamp string offset from *base*."""
    return (base + timedelta(seconds=offset_seconds)).isoformat()


@activity.defn
async def contact_plumber(input: ContactPlumberInput) -> ContactPlumberOutput:
    """
    DEMO MOCK — bi-directional chat session with the plumber service.

    Simulates:
        1. Opening a persistent chat session.
        2. Sending LLM-generated dispatch instructions.
        3. Receiving a series of plumber replies (with realistic delays).
        4. System acknowledgements after key milestones.
        5. Returning the full chat transcript + session metadata.

    Args:
        input: ContactPlumberInput with issue details.

    Returns:
        ContactPlumberOutput containing the chat transcript in ``result``.
    """
    logger.info("contact_plumber [MOCK CHAT] — step_id=%s", input.step_id)

    now = datetime.now(timezone.utc)
    session_id = f"CHAT-{input.issue_id or 'unknown'}-{int(now.timestamp())}"
    elapsed = 0  # running clock for timestamps
    transcript: list[dict] = []

    # ── 1. Open session ──────────────────────────────────────────────────
    transcript.append({
        "role": "system",
        "message": f"Chat session opened — session_id={session_id}",
        "timestamp": _ts(now, elapsed),
    })
    logger.info("  ↳ session opened: %s", session_id)

    # ── 2. Send LLM-generated dispatch instructions ─────────────────────
    dispatch_text = ""
    if input.description:
        prompt = (
            f"Generate concise dispatch instructions for a {input.urgency} urgency "
            f"plumbing issue: {input.description}"
        )
        if input.location:
            prompt += f" at location: {input.location}"

        logger.info("  ↳ generating LLM dispatch text")
        dispatch_text = await _llm_service.generate_report({"problem_statement": prompt})

    elapsed += 1
    transcript.append({
        "role": "system",
        "message": dispatch_text or f"Dispatch request: {input.description}",
        "timestamp": _ts(now, elapsed),
    })

    # ── 3. Simulate plumber replies ──────────────────────────────────────
    for reply in _MOCK_PLUMBER_REPLIES:
        await asyncio.sleep(reply["delay_seconds"])
        elapsed += reply["delay_seconds"]

        # Plumber message
        transcript.append({
            "role": "plumber",
            "message": reply["message"],
            "timestamp": _ts(now, elapsed),
        })
        logger.info("  ↳ plumber: %s", reply["message"][:80])

        # System auto-acknowledgement after each plumber message
        elapsed += 1
        transcript.append({
            "role": "system",
            "message": "Noted. Message logged and forwarded to the municipal dashboard.",
            "timestamp": _ts(now, elapsed),
        })

    # ── 4. Close session ─────────────────────────────────────────────────
    elapsed += 1
    transcript.append({
        "role": "system",
        "message": "Repair confirmed. Closing chat session. A field report will be generated next.",
        "timestamp": _ts(now, elapsed),
    })

    logger.info("  ↳ session closed after %d messages", len(transcript))

    return ContactPlumberOutput(
        step_id=input.step_id,
        service="plumber",
        result={
            "session_id": session_id,
            "session_status": "closed",
            "total_messages": len(transcript),
            "chat_transcript": transcript,
            "plumber_eta": "30 minutes",
            "repair_duration": "45 minutes",
            "repair_status": "completed",
            "pressure_test": "passed — 60 PSI",
        },
        status="completed",
    )
