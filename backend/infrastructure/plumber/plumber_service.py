from abc import ABC, abstractmethod
from typing import Any, Dict

class PlumberInterface(ABC):
    """
    Abstract interface for Plumber services.
    """

    @abstractmethod
    async def contact(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Contact the plumber service.
        """
        pass
