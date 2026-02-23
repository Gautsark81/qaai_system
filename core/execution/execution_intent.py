# core/execution/execution_intent.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import uuid
import hashlib
import json


def _deterministic_execution_id(payload: dict) -> str:
    """
    Deterministic UUID derived from intent payload.
    Ensures replay stability.
    """
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode()
    ).hexdigest()
    return str(uuid.UUID(digest[:32]))


@dataclass(frozen=True)
class ExecutionIntent:
    symbol: str
    side: str
    quantity: int
    price: Optional[float] = None
    venue: str = "PAPER"

    # --- NEW (required by later phases) ---
    strategy_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # --- Core invariant ---
    execution_id: str = field(init=False)

    def __post_init__(self):
        payload = {
            "symbol": self.symbol,
            "side": self.side,
            "quantity": self.quantity,
            "price": self.price,
            "venue": self.venue,
            "strategy_id": self.strategy_id,
            "metadata": self.metadata,
        }

        object.__setattr__(
            self,
            "execution_id",
            _deterministic_execution_id(payload),
        )

    @staticmethod
    def example() -> "ExecutionIntent":
        """
        Test-only helper. Required by execution tests.
        """
        return ExecutionIntent(
            symbol="TEST",
            side="BUY",
            quantity=1,
            price=100.0,
            venue="PAPER",
        )
