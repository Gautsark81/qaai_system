from abc import ABC, abstractmethod
from typing import Any, Dict


class ShadowExecutor(ABC):
    """
    Executes orders in shadow / paper mode.
    """

    @abstractmethod
    def submit_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Accepts a real order payload.
        Returns a synthetic execution result.
        Must never place a live order.
        """
        raise NotImplementedError
