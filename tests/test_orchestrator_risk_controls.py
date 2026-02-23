# tests/test_orchestrator_risk_controls.py
import pytest
from qaai_system.execution.risk_manager import RiskManager
from qaai_system.execution.position_manager import PositionManager
from qaai_system.execution.orchestrator import ExecutionOrchestrator


# -------------------------
# Dummy classes
# -------------------------


class DummyRouter:
    def __init__(self):
        self.last = None

    def route(self, order):
        self.last = order
        # pretend instant fill
        side = order["side"]
        qty = int(order["quantity"])
        price = float(order.get("price", 100.0))
        return {
            "status": "filled",
            "order_id": "X1",
            "fills": [{"side": side, "qty": qty, "price": price}],
            "timestamp": "2025-01-01T00:00:00Z",
        }


class DummyProvider:
    def __init__(self):
        self.cancel_all_called = False

    def cancel_all(self):
        self.cancel_all_called = True
        return [{"order_id": "X1"}]


# -------------------------
# Existing test cases
# -------------------------


def test_kill_switch_blocks_new_orders():
    rm = RiskManager()
    orch = ExecutionOrchestrator(
        router=DummyRouter(),
        risk=rm,
        positions=PositionManager(),
        config={"starting_cash": 1_000_000},
    )
    rm.trigger_kill_switch("test")
    resp = orch.submit_order(
        {"symbol": "AAA", "side": "buy", "quantity": 10, "price": 100.0}
    )
    assert resp["status"] == "blocked"
    assert "KillSwitch" in resp["reason"]


def test_circuit_breaker_blocks_after_drawdown():
    rm = RiskManager(config={"max_drawdown_pct": 1.0})  # 1% max drawdown allowed
    orch = ExecutionOrchestrator(
        router=DummyRouter(),
        risk=rm,
        positions=PositionManager(),
        config={"starting_cash": 100_000},
    )

    # First order (should be filled)
    resp1 = orch.submit_order(
        {"symbol": "AAA", "side": "buy", "quantity": 10, "price": 100.0}
    )
    assert resp1["status"] == "filled"

    # Simulate drawdown
    orch.account_equity_func = lambda: 98_000  # -2%
    orch._peak_equity = 100_000  # Optional, RiskManager should maintain this

    # Second order: causes breaker to trip
    resp2 = orch.submit_order(
        {"symbol": "AAA", "side": "buy", "quantity": 10, "price": 100.0}
    )

    # Third order: should be blocked
    resp3 = orch.submit_order(
        {"symbol": "AAA", "side": "buy", "quantity": 10, "price": 100.0}
    )
    assert resp3["status"] == "blocked"
    assert "Drawdown" in resp3["reason"] or "circuit" in resp3["reason"].lower()


# -------------------------
# Enhanced test cases
# -------------------------


def test_static_kill_switch_raises():
    rm = RiskManager()
    rm.trigger_kill_switch("test")
    config = {"starting_cash": 1_000_000, "risk": {"kill_switch": True}}
    orch = ExecutionOrchestrator(
        router=DummyRouter(), risk=rm, positions=PositionManager(), config=config
    )

    with pytest.raises(RuntimeError, match="KILL_SWITCH_ACTIVE"):
        orch.submit_order(
            {"symbol": "AAPL", "side": "buy", "quantity": 1, "price": 100}
        )


def test_symbol_cap_blocks_order():
    rm = RiskManager()
    orch = ExecutionOrchestrator(
        router=DummyRouter(),
        risk=rm,
        positions=PositionManager(),
        config={"starting_cash": 1_000_000},
    )

    # Force symbol cap check to block
    rm.check_symbol_cap = lambda *args, **kwargs: False

    with pytest.raises(ValueError, match="(?i)symbol cap"):
        orch.submit_order(
            {"symbol": "AAPL", "side": "buy", "quantity": 10, "price": 100}
        )


def test_risk_evaluation_blocks_order():
    rm = RiskManager()
    orch = ExecutionOrchestrator(
        router=DummyRouter(),
        risk=rm,
        positions=PositionManager(),
        config={"starting_cash": 1_000_000},
    )

    # Simulate risk evaluation block with reason
    rm.evaluate_risk = lambda *args, **kwargs: (False, "Too volatile")

    with pytest.raises(ValueError, match="RISK_BLOCK: Too volatile"):
        orch.submit_order(
            {"symbol": "AAPL", "side": "buy", "quantity": 10, "price": 100}
        )


def test_arm_kill_switch_cancels_orders():
    provider = DummyProvider()
    rm = RiskManager()
    orch = ExecutionOrchestrator(
        provider=provider,
        risk=rm,
        positions=PositionManager(),
        config={"starting_cash": 1_000_000},
    )

    count = orch.arm_kill_switch()

    assert provider.cancel_all_called
    assert count == 1
