from typing import Optional
from .plumber_interface import PlumberInterface
from .default_plumber_adapter import DefaultPlumberAdapter

class PlumberFactory:
    """
    Factory for creating PlumberInterface instances.
    """
    _instance = None

    @classmethod
    def get_plumber_service(cls, base_url: Optional[str] = None, api_key: Optional[str] = None) -> PlumberInterface:
        if cls._instance is None:
            cls._instance = DefaultPlumberAdapter(base_url=base_url, api_key=api_key)
        return cls._instance
