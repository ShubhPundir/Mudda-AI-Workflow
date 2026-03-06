"""
External service activities — DEMO MOCK.

Mocks the plumber dispatch as a bi-directional chat session.
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

