from abc import ABC, abstractmethod
from typing import Dict, Any


class OrderManagerBase(ABC):
    """
    Base class for all order managers.
    Enforces interface consistency.
    """

    def __init__(self, *, approved_for_live: bool = False):
        self.approved_for_live = approved_for_live

    @abstractmethod
    def submit_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        raise NotImplementedError
