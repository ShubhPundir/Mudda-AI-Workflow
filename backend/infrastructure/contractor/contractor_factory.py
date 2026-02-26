from typing import Optional
from .contractor_service import ContractorService
from .default_contractor_adapter import DefaultContractorAdapter

class ContractorFactory:
    """
    Factory for creating ContractorService instances.
    """
    _instance = None

    @classmethod
    def get_contractor_service(cls, base_url: Optional[str] = None, api_key: Optional[str] = None) -> ContractorService:
        if cls._instance is None:
            cls._instance = DefaultContractorAdapter(base_url=base_url, api_key=api_key)
        return cls._instance
