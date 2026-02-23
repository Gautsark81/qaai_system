# core/paper/paper_models.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class PaperOrder:
    strategy_id: str
    symbol: str
    side: str  # BUY / SELL
    quantity: int
    price: float
    timestamp: str


@dataclass(frozen=True)
class PaperFill:
    order: PaperOrder
    fill_price: float
    slippage: float
    filled_at: str
