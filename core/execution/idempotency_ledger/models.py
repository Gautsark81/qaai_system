# core/execution/idempotency_ledger/models.py

from dataclasses import dataclass
from datetime import datetime
from typing import Any
import hashlib
import json


@dataclass(frozen=True)
class ExecutionIdempotencyRecord:
    execution_intent_id: str
    strategy_id: str
    symbol: str
    side: str
    quantity: int
    price: float
    timestamp: datetime

    def identity_hash(self) -> str:
        payload = {
            "execution_intent_id": self.execution_intent_id,
            "strategy_id": self.strategy_id,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": self.quantity,
            "price": self.price,
            "timestamp": self.timestamp.isoformat(),
        }

        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
