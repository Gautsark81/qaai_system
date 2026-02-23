import time
from qaai_system.execution.order_router import OrderRouter
from qaai_system.execution.router import ExecutionRouter, DummyRouter

# -----------------------
# Fakes for router tests
# -----------------------
class FakeProviderOK:
    """Simple provider that records submitted orders and simulates status."""

    def __init__(self):
        self.submitted = []
        self.status = {}

    def submit_order(self, order):
        oid = f"ord_{len(self.submitted)+1}"
        self.submitted.append((oid, dict(order)))
        # store a basic status shape
        self.status[oid] = {
            "order_id": oid,
            "status": "FILLED",
            "filled_qty": order.get("quantity", order.get("qty", 0)),
            "avg_price": order.get("price", 100.0),
            "side": order.get("side", "BUY"),
        }
        return oid

    def get_order_status(self, order_id):
        return self.status.get(order_id, {"order_id": order_id, "status": "UNKNOWN"})


class FakeProviderRaises:
    """Provider whose submit_order always raises (to test fallback path)."""

    def submit_order(self, order):
        raise RuntimeError("provider failure")


class FakePolicySingleChunk:
    """Routing policy that always returns a single chunk identical to the plan."""

    def build_order_requests(self, plan):
        return [dict(plan)]


class FakeRiskManagerAllow:
    """Risk manager that always allows trading and always approves plans."""

    def __init__(self, cfg=None):
        self.cfg = cfg or {}
        self.heartbeat_called = 0
        self.evaluated_plans = []

    def heartbeat(self, account_equity=None):
        self.heartbeat_called += 1

    def is_trading_allowed(self, account_equity=None):
        return True

    def evaluate_risk(self, plan, account_equity=None):
        self.evaluated_plans.append(plan)
        return True, "OK"

    def circuit_reason(self):
        return "circuit_ok"


class FakeRiskManagerBlock:
    """Risk manager that disallows trading."""

    def heartbeat(self, account_equity=None):
        pass

    def is_trading_allowed(self, account_equity=None):
        return False

    def evaluate_risk(self, plan, account_equity=None):
        return True, "OK"

    def circuit_reason(self):
        return "circuit_blocked"


class FakeRiskManagerRejectPlan:
    """Risk manager that rejects every plan with a custom reason."""

    def __init__(self, reason="too_risky"):
        self.reason = reason

    def heartbeat(self, account_equity=None):
        pass

    def is_trading_allowed(self, account_equity=None):
        return True

    def evaluate_risk(self, plan, account_equity=None):
        return False, self.reason

    def circuit_reason(self):
        return "circuit_ok"


class FakeRiskManagerEvalRaises:
    """evaluate_risk raises to test conservative rejection path."""

    def heartbeat(self, account_equity=None):
        pass

    def is_trading_allowed(self, account_equity=None):
        return True

    def evaluate_risk(self, plan, account_equity=None):
        raise RuntimeError("risk crash")

    def circuit_reason(self):
        return "circuit_ok"


# -----------------------
# Tests
# -----------------------
def test_order_router_happy_path_and_settle_synthesized_fill():
    provider = FakeProviderOK()
    policy = FakePolicySingleChunk()
    risk = FakeRiskManagerAllow()
    cfg = {"starting_cash": 1_000_000, "risk": {"max_drawdown_pct": None}}

    router = OrderRouter(provider=provider, config=cfg, policy=policy, risk=risk)

    plan = {"symbol": "NIFTY", "side": "BUY", "qty": 10, "price": 100.0}
    resp = router.submit(plan)

    # ParentResponse basics
    assert resp["status"] == "submitted"
    assert isinstance(str(resp), str)
    assert resp.order_id in router._orders  # internal book-keeping

    # The router should have created a routed order with child ids
    child_ids = router.get_child_orders(resp.order_id)
    assert len(child_ids) == 1
    assert child_ids[0].startswith("ord_")

    # Now settle and check aggregate summary; provider returns 'FILLED'
    summary = router.settle([resp.order_id])
    assert resp.order_id in summary
    parent = summary[resp.order_id]
    assert parent["status"] == "FILLED"     # uppercase in settlement
    assert parent["filled_qty"] == 10
    assert parent["planned_qty"] == 10
    assert parent["avg_price"] == 100.0
    assert summary["fill_ratio"] == 1.0
    assert summary["avg_price"] == 100.0


def test_order_router_blocked_by_risk_manager_is_trading_allowed():
    provider = FakeProviderOK()
    policy = FakePolicySingleChunk()
    risk = FakeRiskManagerBlock()
    cfg = {"starting_cash": 1_000_000, "risk": {"max_drawdown_pct": None}}

    router = OrderRouter(provider=provider, config=cfg, policy=policy, risk=risk)

    plan = {"symbol": "NIFTY", "side": "BUY", "qty": 10, "price": 100.0}
    resp = router.submit(plan)

    assert resp["status"] == "blocked"
    # reason should mention circuit or use circuit_reason
    assert "circuit" in resp.get("reason", "")


def test_order_router_blocked_by_drawdown_circuit():
    provider = FakeProviderOK()
    policy = FakePolicySingleChunk()
    risk = FakeRiskManagerAllow()
    cfg = {"starting_cash": 100.0, "risk": {"max_drawdown_pct": 10.0}}

    router = OrderRouter(provider=provider, config=cfg, policy=policy, risk=risk)

    # simulate equity drop of 30%
    router.account_equity = 70.0

    plan = {"symbol": "NIFTY", "side": "BUY", "qty": 10, "price": 100.0}
    resp = router.submit(plan)

    assert resp["status"] == "blocked"
    assert "drawdown" in resp.get("reason", "").lower()


def test_order_router_rejects_plan_if_evaluate_risk_says_no():
    provider = FakeProviderOK()
    policy = FakePolicySingleChunk()
    risk = FakeRiskManagerRejectPlan(reason="too_big")
    cfg = {"starting_cash": 1_000_000, "risk": {"max_drawdown_pct": None}}

    router = OrderRouter(provider=provider, config=cfg, policy=policy, risk=risk)

    plan = {"symbol": "NIFTY", "side": "BUY", "qty": 10, "price": 100.0}
    resp = router.submit(plan)

    assert resp["status"] == "rejected"
    assert resp.get("reason") == "too_big"

def test_order_router_rejects_if_evaluate_risk_raises():
    provider = FakeProviderOK()
    policy = FakePolicySingleChunk()
    risk = FakeRiskManagerEvalRaises()
    cfg = {"starting_cash": 1_000_000, "risk": {"max_drawdown_pct": None}}

    router = OrderRouter(provider=provider, config=cfg, policy=policy, risk=risk)

    plan = {"symbol": "NIFTY", "side": "BUY", "qty": 10, "price": 100.0}
    resp = router.submit(plan)

    assert resp["status"] == "rejected"
    # generic failure reason
    assert "risk" in resp.get("reason", "")

def test_order_router_provider_failure_returns_error_child_id():
    provider = FakeProviderRaises()
    policy = FakePolicySingleChunk()
    risk = FakeRiskManagerAllow()
    cfg = {"starting_cash": 1_000_000, "risk": {"max_drawdown_pct": None}}

    router = OrderRouter(provider=provider, config=cfg, policy=policy, risk=risk)

    plan = {"symbol": "NIFTY", "side": "BUY", "qty": 5, "price": 100.0}
    resp = router.submit(plan)

    assert resp["status"] == "submitted"  # router still returns submitted
    child_ids = router.get_child_orders(resp.order_id)
    assert len(child_ids) == 1

    cid = child_ids[0]
    # Provider failed, but router must still produce a valid child id.
    # Two possibilities:
    #   - Safe client worked  -> something like "sim-..."
    #   - Safe client absent/failed -> "err_..." placeholder
    assert isinstance(cid, str) and cid
    # Ensure it's not a happy-path provider id like 'ord_1'
    assert not cid.startswith("ord_")

def test_execution_router_and_dummy_router_basic_behaviour():
    provider = FakeProviderOK()
    exec_router = ExecutionRouter(provider)

    plan = {"symbol": "NIFTY", "side": "BUY", "qty": 3, "price": 100.0}
    oid = exec_router.submit(plan)
    assert oid.startswith("ord_")

    cancel_resp = exec_router.cancel(oid)
    assert cancel_resp["order_id"] == oid
    assert cancel_resp["status"] == "CANCELLED"

    # DummyRouter always immediately fills
    dummy = DummyRouter()
    resp = dummy.submit(plan)
    assert resp["status"] == "filled"
    cancel_resp = dummy.cancel("xyz")
    assert cancel_resp["status"] == "CANCELLED"
    status_resp = dummy.get_status("xyz")
    assert status_resp["status"] == "FILLED"
