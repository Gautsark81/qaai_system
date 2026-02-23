# core/shadow/execution/shadow_order.py
from dataclasses import dataclass
from enum import Enum


class ShadowOrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


@dataclass(frozen=True)
class ShadowOrder:
    strategy_id: str
    symbol: str
    side: ShadowOrderSide
    quantity: int
    price: float   # deterministic fill price (from market snapshot)
