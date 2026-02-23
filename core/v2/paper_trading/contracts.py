from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class PaperOrder:
    order_id: str
    strategy_id: str
    symbol: str
    side: str  # "BUY" | "SELL"
    quantity: int
    created_at: datetime


@dataclass(frozen=True)
class PaperFill:
    fill_id: str
    order_id: str
    symbol: str
    side: str
    quantity: int
    price: float
    filled_at: datetime


@dataclass(frozen=True)
class PaperTradeCycle:
    """
    One deterministic paper-trading cycle.
    """
    cycle_id: str
    started_at: datetime
    ended_at: datetime

    orders_created: int
    fills_created: int

    pnl_delta: float
