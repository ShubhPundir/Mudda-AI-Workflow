"""
Activities involving human interaction.
"""
import logging
from typing import Any, Dict
from temporalio import activity

logger = logging.getLogger(__name__)

@activity.defn
async def human_feedback_activity(input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Placeholder for human feedback. 
    In production, this might wait for a signal or interact with a UI.
    """
    logger.info("Waiting for human feedback... (simulated)")

    # TODO: implement actual human feedback --> connectivity with backend
    return {
        "approved": True,
        "feedback": "Approved by official",
        "status": "completed"
    }

@activity.defn
async def human_verification_activity(input: Dict[str, Any]) -> Dict[str, Any]:
    """Verification of external service response by a human."""
    logger.info("Human verifying external response...")

    # TODO: implement actual human verification --> connectivity with backend
    return {
        "verified": True,
        "notes": "Work quality verified",
        "status": "completed"
    }
