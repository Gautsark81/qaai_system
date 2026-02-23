import pytest
from typing import Any, Dict

from qaai_system.execution.risk_manager import RiskManager
from qaai_system.execution.orchestrator import ExecutionOrchestrator

# --- Dummy providers / routers for tests ---


class DummyProviderSuccess:
    def __init__(self):
        self._orders = {}
        self._next = 1
        self._account_nav = 100000.0

    def submit_order(self, order: Dict[str, Any]):
        oid = f"ORD{self._next}"
        self._next += 1
        rec = {
            "order_id": oid,
            "symbol": order.get("symbol"),
            "qty": order.get("quantity") or order.get("qty"),
            "price": order.get("price"),
            "status": "SUBMITTED",
            "pnl": 0.0,
        }
        self._orders[oid] = rec
        return {"order_id": oid, "status": "submitted", "symbol": order.get("symbol")}

    def cancel_order(self, oid):
        if oid in self._orders:
            self._orders[oid]["status"] = "CANCELLED"
            return {"status": "cancelled"}
        return {"status": "not_found"}

    def get_order_status(self, oid):
        return self._orders.get(oid, {"status": "UNKNOWN"})

    def get_filled_orders(self):
        return [
            o
            for o in self._orders.values()
            if str(o.get("status", "")).upper() in {"FILLED", "CLOSED"}
        ]


class DummyProviderFail:
    def __init__(self):
        self._orders = {}
        self._next = 1
        self._account_nav = 100000.0

    def submit_order(self, order):
        raise RuntimeError("broker down")

    def cancel_order(self, oid):
        return {"status": "not_found"}


class DummyRouterSuccess:
    def __init__(self):
        self._orders = {}
        self._next = 1

    def submit(self, order: Dict[str, Any]):
        oid = f"RT{self._next}"
        self._next += 1
        rec = {
            "order_id": oid,
            "status": "submitted",
            "symbol": order.get("symbol"),
            "qty": order.get("quantity") or order.get("qty"),
            "price": order.get("price"),
        }
        self._orders[oid] = rec
        return rec

    def cancel(self, oid):
        if oid in self._orders:
            self._orders[oid]["status"] = "CANCELLED"
            return True
        return False

    def place_order(self, order):
        return self.submit(order)


class DummyRouterFail:
    def submit(self, order):
        raise RuntimeError("router error")


# ----------------------------
# Fixtures
# ----------------------------
@pytest.fixture
def base_cfg():
    return {
        "risk": {
            "starting_cash": 100000,
            "max_open_trades": 5,
            "max_position_size_pct": 0.2,
            "max_loss_per_trade": 10000,
            "max_symbol_weight": 0.5,
            "max_order_notional": 50000,
            "max_risk_pct_per_trade": 0.01,
        },
        "starting_cash": 100000,
    }


@pytest.fixture
def orchestrator_success(base_cfg):
    rm = RiskManager(config=base_cfg["risk"])
    provider = DummyProviderSuccess()
    orch = ExecutionOrchestrator(provider=provider, risk=rm, config=base_cfg)
    return orch


@pytest.fixture
def orchestrator_router_fail(base_cfg):
    rm = RiskManager(config=base_cfg["risk"])
    router = DummyRouterFail()
    orch = ExecutionOrchestrator(router=router, risk=rm, config=base_cfg)
    return orch


@pytest.fixture
def orchestrator_provider_fail(base_cfg):
    rm = RiskManager(config=base_cfg["risk"])
    provider = DummyProviderFail()
    orch = ExecutionOrchestrator(provider=provider, risk=rm, config=base_cfg)
    return orch


# ----------------------------
# Tests
# ----------------------------
def test_submit_order_creates_reservation_and_persists(orchestrator_success):
    orch = orchestrator_success
    order = {"symbol": "AAPL", "price": 100, "quantity": 10, "strategy_id": "S1"}
    # submit -> should reserve 1000 notional and persist submitted order
    res = orch.submit_order(order)
    assert res["status"].upper() in {"SUBMITTED", "FILLED"}
    # find order_id
    oid = res.get("order_id")
    assert oid
    stored = orch.provider._orders.get(oid)
    assert stored and stored.get("reserved_by") == "S1"
    assert stored.get("reserved_notional") == pytest.approx(1000.0)


def test_router_exception_releases_reservation(orchestrator_router_fail):
    orch = orchestrator_router_fail
    order = {"symbol": "AAPL", "price": 100, "quantity": 10, "strategy_id": "S_X"}
    # router raises -> orchestrator should release reservation and return error
    res = orch.submit_order(order)
    assert res["status"] == "ERROR"
    # ensure no lingering reservations
    reservations = orch.risk.get_reservations()
    # no reservations or at least none for S_X
    assert all(not (k[0] == "S_X") for k in reservations.keys())


def test_provider_exception_releases_reservation(orchestrator_provider_fail):
    orch = orchestrator_provider_fail
    order = {
        "symbol": "AAPL",
        "price": 200,
        "quantity": 300,
        "strategy_id": "S2",
    }  # notional 60k > max_order_notional -> should block at reservation stage
    with pytest.raises(ValueError):
        orch.submit_order(order)
    # ensure reservation not stored
    assert all(not (k[0] == "S2") for k in orch.risk.get_reservations().keys())


def test_cancel_releases_reservation(orchestrator_success):
    orch = orchestrator_success
    order = {
        "symbol": "TSLA",
        "price": 50,
        "quantity": 200,
        "strategy_id": "S3",
    }  # notional 10k
    res = orch.submit_order(order)
    oid = res.get("order_id")
    assert oid
    # ensure reservation exists
    stored = orch.provider._orders.get(oid)
    assert stored.get("reserved_by") == "S3"
    # cancel
    ok = orch.cancel_order(oid)
    assert ok
    # reservation should be released
    reservations = orch.risk.get_reservations()
    assert all(not (k[0] == "S3") for k in reservations.keys())


def test_kill_switch_blocks(orchestrator_success):
    orch = orchestrator_success
    orch.risk.set_kill_switch(True)
    order = {"symbol": "AAPL", "price": 10, "quantity": 1, "strategy_id": "S1"}
    resp = orch.submit_order(order)
    assert resp["status"] == "blocked"
    orch.risk.clear_kill_switch()
