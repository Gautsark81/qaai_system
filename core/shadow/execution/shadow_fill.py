# core/shadow/execution/shadow_fill.py
from dataclasses import dataclass


@dataclass(frozen=True)
class ShadowFill:
    symbol: str
    quantity: int
    price: float
