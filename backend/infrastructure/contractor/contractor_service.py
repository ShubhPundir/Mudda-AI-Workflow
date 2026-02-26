from abc import ABC, abstractmethod
from typing import Any, Dict

class ContractorService(ABC):
    """
    Abstract interface for Contractor services.
    """

    @abstractmethod
    async def contact(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Contact the contractor service.
        """
        pass
