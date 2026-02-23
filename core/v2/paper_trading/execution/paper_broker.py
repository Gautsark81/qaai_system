from __future__ import annotations

from datetime import datetime
from typing import Callable

from core.v2.paper_trading.contracts import PaperOrder, PaperFill


class PaperBroker:
    """
    Deterministic paper broker.

    Converts PaperOrders into PaperFills using a pricing function.
    """

    def __init__(
        self,
        *,
        price_provider: Callable[[str, datetime], float],
    ):
        self._price_provider = price_provider

    def execute(self, order: PaperOrder) -> PaperFill:
        price = self._price_provider(order.symbol, order.created_at)

        return PaperFill(
            fill_id=f"fill-{order.order_id}",
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=price,
            filled_at=order.created_at,
        )
