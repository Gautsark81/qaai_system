from __future__ import annotations

from typing import List

from core.v2.paper_trading.contracts import PaperOrder
from core.v2.paper_trading.orders.order import PaperOrderRequest


class OrderBook:
    """
    In-memory order book for paper trading.
    """

    def __init__(self):
        self._orders: List[PaperOrder] = []

    def add(self, order: PaperOrder) -> None:
        self._orders.append(order)

    def all_orders(self) -> List[PaperOrder]:
        return list(self._orders)
