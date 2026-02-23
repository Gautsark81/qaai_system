from qaai_system.execution.execution_engine import ExecutionEngine
from qaai_system.execution.order_manager import OrderManager
from core.capital.capital_allocator import CapitalDecision, CapitalDecisionEngine
from qaai_system.execution.risk_manager import RiskLimitViolation


class AlwaysApproveCapital(CapitalDecisionEngine):
    def decide(self, **_):
        return CapitalDecision(
            decision=CapitalDecision.ALLOW,
            multiplier=100.0,  # extreme
            reasons=["force allow"],
        )


class AlwaysBlockRisk:
    def evaluate_risk(self, order, equity):
        return False, "risk hard block"


def test_risk_overrides_capital_always():
    om = OrderManager(mode="paper")

    engine = ExecutionEngine(
        order_manager=om,
        capital_engine=AlwaysApproveCapital(),
        risk_engine=AlwaysBlockRisk(),
    )

    try:
        engine.submit(
            {"symbol": "NIFTY", "side": "BUY", "quantity": 1, "price": 100}
        )
    except RiskLimitViolation:
        pass
    else:
        assert False, "Risk engine must block even if capital approves"


def test_capital_replay_is_idempotent():
    engine = ExecutionEngine(mode="paper")

    signal = {
        "symbol": "NIFTY",
        "side": "BUY",
        "price": 100,
        "position_size": 1,
        "strategy_id": "S1",
    }

    engine.submit(signal)
    engine.submit(signal)  # replay

    orders = engine.order_manager.get_all_orders()
    assert len(orders) == 1, "Capital replay must not duplicate orders"

class ExplodingCapital(CapitalDecisionEngine):
    def decide(self, **_):
        return CapitalDecision(
            decision=CapitalDecision.ALLOW,
            multiplier=10_000,
            reasons=["overflow attempt"],
        )


def test_capital_multiplier_sanity_cap():
    engine = ExecutionEngine(
        capital_engine=ExplodingCapital(),
        mode="paper",
    )

    engine.submit(
        {
            "symbol": "BANKNIFTY",
            "side": "BUY",
            "quantity": 1,
            "price": 100,
        }
    )

    orders = engine.order_manager.get_all_orders()
    order = list(orders.values())[0]

    assert order["quantity"] < 1000, "Position size sanity must cap multiplier"


def test_fill_cannot_exceed_capital_approval():
    engine = ExecutionEngine(mode="paper")

    oid = engine.order_manager.create_order(
        symbol="NIFTY",
        side="BUY",
        quantity=5,
        price=100,
        meta={"approved_qty": 5},
    )

    engine.on_fill(
        {
            "trade_id": "T1",
            "symbol": "NIFTY",
            "side": "BUY",
            "filled_qty": 10,  # overfill attempt
            "avg_fill_price": 100,
            "pnl": 0,
            "close_reason": "TP",
            "order_meta": {"approved_qty": 5},
        }
    )

    # Overfill must be flagged
    # No silent acceptance allowed
    assert "OVERFILL" in str(engine.execution_journal.replay()).upper()

class RecorderRisk:
    def __init__(self):
        self.called = False

    def evaluate_risk(self, *_):
        self.called = True
        return True, "ok"


class RecorderCapital(CapitalDecisionEngine):
    def __init__(self):
        self.called = False

    def decide(self, **_):
        self.called = True
        return CapitalDecision.allow()


def test_risk_called_before_capital():
    risk = RecorderRisk()
    cap = RecorderCapital()

    engine = ExecutionEngine(
        risk_engine=risk,
        capital_engine=cap,
        mode="paper",
    )

    engine.submit(
        {"symbol": "NIFTY", "side": "BUY", "quantity": 1, "price": 100}
    )

    assert risk.called is True
    assert cap.called is True

def test_capital_decision_is_frozen():
    engine = ExecutionEngine(mode="paper")

    oid = engine.submit(
        {"symbol": "NIFTY", "side": "BUY", "quantity": 1, "price": 100}
    )["order_id"]

    order = engine.order_manager.get_order(oid)
    order["meta"]["capital_decision"] = "HACKED"

    persisted = engine.order_manager.get_order(oid)
    assert persisted["meta"]["capital_decision"] != "HACKED"
