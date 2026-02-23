from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PaperOrderRequest:
    """
    Intent-level order request before broker execution.
    """
    strategy_id: str
    symbol: str
    side: str
    quantity: int
    created_at: datetime
