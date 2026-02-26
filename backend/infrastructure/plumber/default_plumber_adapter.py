import logging
from typing import Any, Dict, Optional
from .plumber_service import PlumberService

logger = logging.getLogger(__name__)

class DefaultPlumberAdapter(PlumberService):
    """
    Default implementation for the Plumber API.
    """

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url or "https://api.plumber-service.example.com"
        self.api_key = api_key

    async def contact(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("DefaultPlumberAdapter.contact — inputs=%s", inputs)
        return {
            "status": "request_submitted",
            "service": "plumber",
            "request_id": f"PLB-{inputs.get('issue_id', 'unknown')}",
            "message": "Plumber service request submitted successfully",
            "inputs_received": inputs,
        }
