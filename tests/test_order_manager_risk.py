# tests/test_order_manager_risk.py
import pytest
import types
from qaai_system.execution.order_manager_with_risk import OrderManagerWithRisk
from qaai_system.execution.risk_manager import RiskManager, RiskConfig, RiskLimitViolation

class DummyOrderManager:
    def __init__(self):
        self.submitted = []

    def submit_order(self, order):
        self.submitted.append(order)
        return {"status": "submitted", "order_id": "dummy-1"}

def test_order_manager_with_risk_allows_good_orders(tmp_path):
    cfg = RiskConfig(symbol_caps={"FOO": 100}, max_portfolio_notional=10000, daily_loss_limit=1000)
    rm = RiskManager(cfg)
    # simple portfolio state getter
    def state_getter():
        return {"positions": {"FOO": 0}, "notional": 0.0, "daily_pnl": 0.0}
    inner = DummyOrderManager()
    wrapped = OrderManagerWithRisk(inner, rm, state_getter)
    order = {"symbol": "FOO", "side": "BUY", "qty": 10, "price": 10}
    res = wrapped.submit_order(order)
    assert res["status"] == "submitted"
    assert inner.submitted[0] == order

def test_order_manager_with_risk_blocks_bad_orders(tmp_path):
    cfg = RiskConfig(symbol_caps={"FOO": 5})
    rm = RiskManager(cfg)
    def state_getter():
        return {"positions": {"FOO": 0}, "notional": 0.0, "daily_pnl": 0.0}
    inner = DummyOrderManager()
    wrapped = OrderManagerWithRisk(inner, rm, state_getter)
    order = {"symbol": "FOO", "side": "BUY", "qty": 10, "price": 10}
    with pytest.raises(RiskLimitViolation):
        wrapped.submit_order(order)
    assert inner.submitted == []
