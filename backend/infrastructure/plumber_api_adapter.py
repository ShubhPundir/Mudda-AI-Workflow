"""
Plumber external service API adapter.

Wraps calls to the external plumber/plumbing service provider API.
No Temporal decorators — this is a plain infrastructure wrapper.
"""
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class PlumberAPIAdapter:
    """
    Adapter for the external plumber service API.

    Replace the placeholder implementation with actual HTTP calls
    to your plumber service provider.
    """

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Args:
            base_url: Base URL of the plumber service API.
            api_key: API key for authentication.
        """
        self.base_url = base_url or "https://api.plumber-service.example.com"
        self.api_key = api_key

    async def contact(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Contact the plumber service with a request.

        Args:
            inputs: Request payload containing issue details, location,
                    urgency, and any other relevant data.

        Returns:
            Dict with service response including request_id, status,
            estimated_arrival, etc.

        Raises:
            RuntimeError: If the external API call fails.
        """
        logger.info("Contacting plumber service — inputs=%s", inputs)

        # ------------------------------------------------------------------
        # TODO: Replace with actual HTTP call, e.g.:
        #
        # import httpx
        # async with httpx.AsyncClient() as client:
        #     resp = await client.post(
        #         f"{self.base_url}/requests",
        #         json=inputs,
        #         headers={"Authorization": f"Bearer {self.api_key}"},
        #     )
        #     resp.raise_for_status()
        #     return resp.json()
        # ------------------------------------------------------------------

        return {
            "status": "request_submitted",
            "service": "plumber",
            "request_id": f"PLB-{inputs.get('issue_id', 'unknown')}",
            "message": "Plumber service request submitted successfully",
            "inputs_received": inputs,
        }
