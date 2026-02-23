from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class ExecutionStatus(str, Enum):
    NEW = "NEW"
    PARTIAL = "PARTIAL"
    FILLED = "FILLED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class ExecutionEvent:
    """
    Phase 14.1 — Canonical execution fact.

    Immutable, append-only, replay-safe.
    """

    order_id: str
    symbol: str
    requested_qty: int
    filled_qty: int
    avg_price: Optional[float]
    status: ExecutionStatus
    exchange_ts: datetime
    system_ts: datetime
    reason: Optional[str] = None

    def fill_ratio(self) -> float:
        if self.requested_qty <= 0:
            return 0.0
        return self.filled_qty / self.requested_qty

    def is_terminal(self) -> bool:
        return self.status in {
            ExecutionStatus.FILLED,
            ExecutionStatus.REJECTED,
            ExecutionStatus.CANCELLED,
        }
