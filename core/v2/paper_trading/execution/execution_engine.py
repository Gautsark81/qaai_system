from __future__ import annotations

from typing import List

from core.v2.paper_trading.contracts import PaperOrder, PaperFill
from core.v2.paper_trading.execution.paper_broker import PaperBroker
from core.v2.paper_trading.orders.order import PaperOrderRequest
from core.v2.paper_trading.orders.order_book import OrderBook


class ExecutionEngine:
    """
    Routes paper orders to the paper broker and records them.
    """

    def __init__(self, *, broker: PaperBroker, order_book: OrderBook):
        self._broker = broker
        self._order_book = order_book

    def submit(self, request: PaperOrderRequest) -> PaperFill:
        order = PaperOrder(
            order_id=f"order-{len(self._order_book.all_orders()) + 1}",
            strategy_id=request.strategy_id,
            symbol=request.symbol,
            side=request.side,
            quantity=request.quantity,
            created_at=request.created_at,
        )

        self._order_book.add(order)
        return self._broker.execute(order)
