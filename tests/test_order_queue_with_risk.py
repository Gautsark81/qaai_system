# tests/test_order_queue_with_risk.py
import pytest
from infra.order_queue import OrderQueue


class DummyProvider:
    def __init__(self, nav=10000, positions=None):
        self._account_nav = nav
        self._positions = positions or {}
        self._connected = True
        self.submissions = []

    def submit_order(self, order):
        # record and return filled
        self.submissions.append(order)
        return {
            "status": "filled",
            "order_id": "ord_x",
            "filled_qty": int(order.get("quantity") or order.get("qty") or 0),
            "price": order.get("price"),
        }

    def get_account_nav(self):
        return float(self._account_nav)

    def get_positions(self):
        return dict(self._positions)

    def connect(self):
        self._connected = True
        return True

    def is_connected(self):
        return bool(self._connected)


def test_order_queue_blocks_on_circuit_breaker():
    class DenyRisk:
        def is_trading_allowed(self, account_equity=None):
            return False

    prov = DummyProvider(nav=100000)
    oq = OrderQueue(provider=prov, risk_manager=DenyRisk())
    with pytest.raises(ValueError, match="Trading not allowed"):
        oq.submit({"symbol": "AAA", "side": "buy", "quantity": 1, "price": 10})


def test_order_queue_blocks_on_symbol_cap():
    # risk manager with max_symbol_weight small
    class RM:
        def __init__(self):
            self.config = {"max_symbol_weight": 0.05}  # 5% of NAV allowed per symbol

        def is_trading_allowed(self, account_equity=None):
            return True

    # set provider NAV 10000, existing position 45 shares at 100 -> exposure 4500
    prov = DummyProvider(nav=10000, positions={"SYM": 45, "__last_price__:SYM": 100})
    oq = OrderQueue(provider=prov, risk_manager=RM())
    # attempt to buy 10 shares at 100 -> projected (45+10)*100 = 5500 which > 10000*0.05=500 -> should raise
    with pytest.raises(ValueError, match="Symbol cap exceeded for SYM"):
        oq.submit({"symbol": "SYM", "side": "buy", "quantity": 10, "price": 100})
