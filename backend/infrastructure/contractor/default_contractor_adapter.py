import logging
from typing import Any, Dict, Optional
from .contractor_interface import ContractorInterface

logger = logging.getLogger(__name__)

class DefaultContractorAdapter(ContractorInterface):
    """
    Default implementation for the Contractor API.
    """

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url or "https://api.contractor-service.mudda.dev"
        self.api_key = api_key

    async def contact(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("DefaultContractorAdapter.contact — inputs=%s", inputs)
        return {
            "status": "request_submitted",
            "service": "contractor",
            "request_id": f"CTR-{inputs.get('issue_id', 'unknown')}",
            "message": "Contractor service request submitted successfully",
            "inputs_received": inputs,
        }
