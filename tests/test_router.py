# tests/test_router.py
from qaai_system.execution.order_router import OrderRouter

class DummyProvider:
    def __init__(self):
        self.orders = {}
        self.counter = 0

    def submit_order(self, order):
        self.counter += 1
        oid = f"child_{self.counter}"
        self.orders[oid] = {
            "status": "submitted",
            "qty": order.get("quantity", 0),
            "price": float(order.get("price", 0.0)),  # fixed: store true price
        }
        return oid

    def get_order_status(self, oid):
        if oid not in self.orders:
            return {"status": "unknown"}
        o = self.orders[oid]
        return {
            "status": "filled",
            "filled_qty": o["qty"],
            "avg_price": o["price"],
            "side": "buy",
        }


def test_parent_response_dict_and_str_behavior():
    resp = ParentResponse("abc123", status="submitted", fill_ratio=0.5)
    assert resp["status"] == "submitted"
    assert "status" in resp
    assert resp.get("fill_ratio") == 0.5
    assert str(resp) == "abc123"
    assert repr(resp).startswith("ParentResponse(")


def test_router_submit_and_settle_full_fill():
    provider = DummyProvider()
    router = OrderRouter(provider=provider, config={"starting_cash": 100000})
    plan = {"symbol": "AAPL", "side": "buy", "qty": 10, "price": 150}

    resp = router.submit(plan)
    assert isinstance(resp, ParentResponse)
    assert resp["status"] == "submitted"
    assert resp.get("fill_ratio") == 0.0

    # settle should mark FILLED with ratio 1.0
    settlement = router.settle([resp])
    parent_data = settlement[resp.order_id]
    assert parent_data["status"] == "FILLED"
    assert parent_data["filled_qty"] == 10
    assert parent_data["fill_ratio"] == 1.0
    assert parent_data["avg_price"] == 150


def test_router_handles_rejected_due_to_risk(monkeypatch):
    provider = DummyProvider()
    router = OrderRouter(provider=provider, config={"starting_cash": 100000})

    # patch risk to always reject
    monkeypatch.setattr(
        router.risk, "evaluate_risk", lambda *a, **k: (False, "Too risky")
    )

    resp = router.submit({"symbol": "TSLA", "side": "sell", "qty": 5, "price": 200})
    assert resp["status"] == "rejected"
    assert "Too risky" in resp.get("reason")


def test_router_settle_with_no_fills_creates_fallback_fill():
    provider = DummyProvider()
    router = OrderRouter(provider=provider, config={"starting_cash": 100000})
    plan = {"symbol": "MSFT", "side": "buy", "qty": 5, "price": 300}

    resp = router.submit(plan)
    # manually wipe provider orders so no fills returned
    provider.orders.clear()

    settlement = router.settle([resp])
    parent_data = settlement[resp.order_id]
    assert parent_data["status"] in {"FILLED", "OPEN"}  # fallback creates a fill
    assert parent_data["planned_qty"] == 5
    assert "fill_ratio" in parent_data
    assert isinstance(parent_data["fills"], list)


def test_execution_router_lightweight_submit():
    provider = DummyProvider()
    exec_router = ExecutionRouter(provider)
    oid = exec_router.submit({"symbol": "NFLX", "side": "buy", "quantity": 2})
    assert oid.startswith("child_")
