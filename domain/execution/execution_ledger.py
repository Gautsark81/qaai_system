from typing import Dict, Optional


class ExecutionLedger:
    """
    In-memory reference ledger (pluggable to DB later).
    intent_id -> broker_order_id
    """

    def __init__(self):
        self._ledger: Dict[str, str] = {}

    def record(self, intent_id: str, broker_order_id: str) -> None:
        self._ledger[intent_id] = broker_order_id

    def exists(self, intent_id: str) -> bool:
        return intent_id in self._ledger

    def get(self, intent_id: str) -> Optional[str]:
        return self._ledger.get(intent_id)
