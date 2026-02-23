from typing import Dict, Any
from .order_manager_base import OrderManagerBase


class LiveOrderManager(OrderManagerBase):
    """
    Live trading manager.
    HARD BLOCKED unless approved_for_live=True.
    """

    def submit_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        if not self.approved_for_live:
            raise RuntimeError("Live trading not approved")

        # Broker call will be injected later
        raise NotImplementedError("Live broker integration pending")

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        if not self.approved_for_live:
            raise RuntimeError("Live trading not approved")

        raise NotImplementedError("Live broker integration pending")
