"""
Contractor external service API adapter.

Wraps calls to the external contractor service provider API.
No Temporal decorators — this is a plain infrastructure wrapper.
"""
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ContractorAPIAdapter:
    """
    Adapter for the external contractor service API.

    Replace the placeholder implementation with actual HTTP calls
    to your contractor service provider.
    """

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Args:
            base_url: Base URL of the contractor service API.
            api_key: API key for authentication.
        """
        self.base_url = base_url or "https://api.contractor-service.mudda.dev"
        self.api_key = api_key

    async def contact(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Contact the contractor service with a request.

        Args:
            inputs: Request payload containing project details, scope,
                    budget, timeline, and any other relevant data.

        Returns:
            Dict with service response including request_id, status,
            estimated_timeline, etc.

        Raises:
            RuntimeError: If the external API call fails.
        """
        logger.info("Contacting contractor service — inputs=%s", inputs)

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
            "service": "contractor",
            "request_id": f"CTR-{inputs.get('issue_id', 'unknown')}",
            "message": "Contractor service request submitted successfully",
            "inputs_received": inputs,
        }
