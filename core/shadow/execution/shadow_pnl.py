# core/shadow/execution/shadow_pnl.py
from dataclasses import dataclass
from typing import Dict
from core.shadow.execution.shadow_position import ShadowPosition


@dataclass
class ShadowPnL:
    realized: float = 0.0
    unrealized: float = 0.0

    def mark_to_market(
        self,
        positions: Dict[str, ShadowPosition],
        prices: Dict[str, float],
    ) -> None:
        self.unrealized = 0.0
        for symbol, pos in positions.items():
            if symbol in prices:
                self.unrealized += (prices[symbol] - pos.avg_price) * pos.quantity
