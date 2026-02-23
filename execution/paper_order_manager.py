import uuid
from typing import Dict, Any
from .order_manager_base import OrderManagerBase


class PaperOrderManager(OrderManagerBase):
    """
    Safe paper trading manager.
    NEVER sends orders to a broker.
    """

    def submit_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "ok",
            "mode": "paper",
            "order_id": f"paper-{uuid.uuid4()}",
            "filled": order.get("quantity", 0),
        }

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        return {
            "status": "cancelled",
            "mode": "paper",
            "order_id": order_id,
        }
