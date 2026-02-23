# demo/fake_broker.py

from dataclasses import dataclass
from modules.brokers.interface import Broker


@dataclass
class FakeOrder:
    broker_order_id: str


class FakeBroker(Broker):
    def submit_market_order(self, *, symbol, side, quantity, client_order_id):
        print(f"[FAKE BROKER] {side} {quantity} {symbol} ({client_order_id})")
        return FakeOrder(broker_order_id=f"FAKE-{client_order_id}")
