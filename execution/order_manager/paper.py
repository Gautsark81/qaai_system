from typing import Dict, Any
from execution.order_manager.base import OrderManager
from qaai_system.execution.order_manager.base import OrderManager
from qaai_system.execution.execution_journal import ExecutionJournal

import uuid


class PaperOrderManager(OrderManager):
    def __init__(self, provider, journal: ExecutionJournal):
        self.provider = provider
        self.journal = journal
        self._seen_orders = set()

        # Replay journal for idempotency
        for rec in self.journal.replay():
            if rec.get("event") == "SUBMIT":
                self._seen_orders.add(rec["order_id"])

    def submit(self, order: Dict[str, Any]) -> Dict[str, Any]:
        # Idempotency key
        order_id = order.get("order_id") or f"paper_{uuid.uuid4().hex[:8]}"

        if order_id in self._seen_orders:
            return {"order_id": order_id, "status": "DUPLICATE"}

        self.journal.append({
            "event": "SUBMIT",
            "order_id": order_id,
            "order": order,
        })

        self._seen_orders.add(order_id)

        # Paper provider executes deterministically
        self.provider._orders[order_id] = dict(order)
        self.provider._orders[order_id]["order_id"] = order_id
        self.provider._orders[order_id]["status"] = "FILLED"

        return {"order_id": order_id, "status": "FILLED"}

    def cancel(self, order_id: str) -> Dict[str, Any]:
        return {"order_id": order_id, "status": "CANCELLED"}

    def get_status(self, order_id: str) -> Dict[str, Any]:
        return self.provider._orders.get(
            order_id, {"order_id": order_id, "status": "UNKNOWN"}
        )

    def poll(self) -> None:
        # Paper execution is synchronous
        return
