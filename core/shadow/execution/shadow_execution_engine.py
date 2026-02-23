# core/shadow/execution/shadow_execution_engine.py
from typing import Dict, List

from core.shadow.execution.shadow_order import ShadowOrder, ShadowOrderSide
from core.shadow.execution.shadow_fill import ShadowFill
from core.shadow.execution.shadow_position import ShadowPosition
from core.shadow.execution.shadow_pnl import ShadowPnL


class ShadowExecutionEngine:
    """
    Capital-free, deterministic execution mirror.

    HARD RULES:
    - No broker calls
    - No capital
    - Deterministic fills only
    """

    def __init__(self):
        self.positions: Dict[str, ShadowPosition] = {}
        self.fills: List[ShadowFill] = []
        self.pnl = ShadowPnL()

    def process_order(self, order: ShadowOrder) -> ShadowFill:
        pos = self.positions.get(order.symbol)
        if pos is None:
            pos = ShadowPosition(symbol=order.symbol)
            self.positions[order.symbol] = pos

        fill_qty = (
            order.quantity
            if order.side == ShadowOrderSide.BUY
            else -order.quantity
        )

        pos.apply_fill(fill_qty, order.price)

        fill = ShadowFill(
            symbol=order.symbol,
            quantity=fill_qty,
            price=order.price,
        )
        self.fills.append(fill)
        return fill

    def mark_to_market(self, prices: Dict[str, float]) -> None:
        self.pnl.mark_to_market(self.positions, prices)
