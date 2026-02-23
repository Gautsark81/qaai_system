# modules/brokers/interface.py

from abc import ABC, abstractmethod
from typing import Protocol


class BrokerOrder(Protocol):
    broker_order_id: str


class Broker(ABC):
    @abstractmethod
    def submit_market_order(
        self,
        *,
        symbol: str,
        side: str,
        quantity: int,
        client_order_id: str,
    ) -> BrokerOrder:
        """
        Side-effectful broker call.
        Must be idempotent w.r.t client_order_id.
        """
        raise NotImplementedError
