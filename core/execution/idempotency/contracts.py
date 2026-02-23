from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any
import hashlib
import json


@dataclass(frozen=True)
class ExecutionIdempotencyKey:
    """
    Canonical, deterministic idempotency key for execution.

    This key guarantees EXACTLY-ONCE execution semantics
    across retries, restarts, brokers, and replays.
    """

    execution_intent_id: str
    strategy_id: str
    symbol: str
    side: str  # BUY / SELL
    quantity: int
    pricing_mode: str  # MARKET / LIMIT
    price: Optional[float]
    market_session: str  # NSE session

    def to_canonical_dict(self) -> Dict[str, Any]:
        """
        Canonical representation used for hashing.
        Order and formatting are STRICT.
        """
        return {
            "execution_intent_id": self.execution_intent_id,
            "strategy_id": self.strategy_id,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": self.quantity,
            "pricing_mode": self.pricing_mode,
            "price": self.price,
            "market_session": self.market_session,
        }

    def to_canonical_json(self) -> str:
        """
        Canonical JSON encoding.
        - Sorted keys
        - No whitespace ambiguity
        """
        return json.dumps(
            self.to_canonical_dict(),
            sort_keys=True,
            separators=(",", ":"),
        )

    def hash(self) -> str:
        """
        Stable SHA256 hash of the canonical execution identity.
        """
        payload = self.to_canonical_json().encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def __str__(self) -> str:
        return self.hash()
