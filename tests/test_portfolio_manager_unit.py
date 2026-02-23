from qaai_system.execution.portfolio_manager import PortfolioManager
from tests.conftest import DummyStrategy as BaseDummyStrategy


class DummyStrategy(BaseDummyStrategy):
    """Extend the shared DummyStrategy to capture trade feedback."""

    def __init__(self, sid, orders=None):  # ✅ make orders optional
        super().__init__(sid, orders or [])

    def on_trade_result(self, trade):
        self.last_trade = trade


def test_register_and_list():
    pm = PortfolioManager()
    s = DummyStrategy("alpha")
    pm.register_strategy(s)
    listed = pm.list_strategies()
    assert any(x["id"] == "alpha" for x in listed)


def test_generate_portfolio_plan_merges():
    s1 = DummyStrategy("s1", [{"symbol": "X", "side": "buy", "quantity": 5}])
    s2 = DummyStrategy("s2", [{"symbol": "X", "side": "buy", "quantity": 10}])
    pm = PortfolioManager()
    pm.register_strategy(s1)
    pm.register_strategy(s2)
    plan = pm.generate_portfolio_plan({})
    assert len(plan) == 1
    assert plan[0]["quantity"] == 15


def test_record_trade_result_updates_feedback_and_weights():
    pm = PortfolioManager()
    s = DummyStrategy("s1")
    pm.register_strategy(s)

    trade = {
        "strategy_id": "s1",
        "symbol": "X",
        "qty": 1,
        "price": 100,
        "pnl": 50.0,
        "win": True,
    }
    pm.record_trade_result(trade)

    metrics = pm.get_strategy_metrics("s1")
    assert metrics["trades"] == 1
    assert metrics["wins"] == 1
    assert metrics["pnl"] == 50.0
    assert "s1" in pm.strategy_weights
    assert pm.strategy_weights["s1"] > 0
    assert hasattr(s, "last_trade")


def test_feedback_updates_strategy_weights():
    pm = PortfolioManager()
    strat = DummyStrategy("s1")
    pm.register_strategy(strat)

    # Record a big positive trade
    pm.record_trade_result(
        {
            "strategy_id": "s1",
            "symbol": "X",
            "qty": 1,
            "price": 100,
            "pnl": 50.0,
            "win": True,
        }
    )
    w1 = pm.strategy_weights["s1"]

    # Record a negative trade, weight should adjust downward
    pm.record_trade_result(
        {
            "strategy_id": "s1",
            "symbol": "X",
            "qty": 1,
            "price": 100,
            "pnl": -50.0,
            "win": False,
        }
    )
    w2 = pm.strategy_weights["s1"]

    assert w2 == w1  # weight decreased after loss
    assert pm.get_strategy_metrics("s1")["trades"] >= 2


def test_register_strategy_with_feedback_links_hooks():
    class FeedbackStrat:
        def __init__(self):
            self.results = []

        def on_trade_result(self, report):
            self.results.append(report)

    pm = PortfolioManager()
    fs = FeedbackStrat()
    pm.register_strategy("fs", fs)
    pm.register_strategy_with_feedback("fs", fs)

    pm.record_trade_result(
        {
            "strategy_id": "fs",
            "symbol": "Y",
            "qty": 2,
            "price": 50,
            "pnl": 20,
            "win": True,
        }
    )

    assert fs.results  # feedback was forwarded
    assert "pnl" in fs.results[0]


def test_unregister_strategy_removes_from_registry():
    pm = PortfolioManager()
    s = DummyStrategy("alpha")
    pm.register_strategy(s)
    assert "alpha" in pm.strategies

    pm.unregister_strategy("alpha")
    assert "alpha" not in pm.strategies


def test_aggregate_and_net_merges_and_caps():
    pm = PortfolioManager()
    plans = [
        {"symbol": "X", "side": "buy", "qty": 3, "strategy": "s1"},
        {"symbol": "X", "side": "buy", "quantity": 2, "strategy": "s2"},
    ]
    out = pm.aggregate_and_net(plans, account_equity=1000)
    assert len(out) == 1
    assert out[0]["quantity"] == 5
    assert "s1" in out[0]["strategies"]
    assert "s2" in out[0]["strategies"]


def test_risk_manager_filters_orders():
    class DummyRiskManager:
        def filter_orders(self, orders):
            return [o for o in orders if o["symbol"] != "BAD"]

    pm = PortfolioManager(risk_manager=DummyRiskManager())
    s = DummyStrategy(
        "s1",
        [
            {"symbol": "BAD", "side": "buy", "quantity": 5},
            {"symbol": "GOOD", "side": "buy", "quantity": 10},
        ],
    )
    pm.register_strategy(s)

    plan = pm.generate_portfolio_plan({}, account_equity=1000)
    assert all(o["symbol"] != "BAD" for o in plan)
    assert any(o["symbol"] == "GOOD" for o in plan)


def test_bracket_attach_called_on_orders(monkeypatch):
    class DummyBM:
        def __init__(self):
            self.registered = []

        def register_bracket(self, **kwargs):
            self.registered.append(kwargs)

    bm = DummyBM()
    orch = type("O", (), {"bracket_manager": bm})()
    pm = PortfolioManager(orchestrator=orch)

    order = {
        "symbol": "AAA",
        "side": "buy",
        "quantity": 1,
        "price": 100.0,
        "take_profit": 120.0,
        "stop_loss": 90.0,
        "trailing_pct": 0.05,
    }
    s = DummyStrategy("s1", [order])
    pm.register_strategy(s)

    plan = pm.generate_portfolio_plan({}, account_equity=1000)
    assert plan  # order survives
    assert bm.registered  # bracket got registered
    r = bm.registered[0]
    assert r["symbol"] == "AAA"
    assert r["qty"] == 1
