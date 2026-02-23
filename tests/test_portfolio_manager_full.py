# tests/test_portfolio_manager_full.py
from qaai_system.execution.strategy_base import StrategyBase
from qaai_system.execution.portfolio_manager import PortfolioManager
from typing import List, Dict, Any


class DummyStrategy(StrategyBase):
    def __init__(
        self,
        sid: str,
        orders: List[Dict[str, Any]],
        allocation=1.0,
        per_symbol_cap=None,
    ):
        super().__init__(sid, allocation=allocation, per_symbol_cap=per_symbol_cap)
        self._orders = orders
        self.received_feedback = []

    def generate_orders(self, market_data):
        # return shallow copies to avoid accidental cross-test mutation
        return [dict(o) for o in self._orders]

    def on_feedback(self, execution_report):
        self.received_feedback.append(execution_report)


class DummyRiskManager:
    def __init__(self):
        self.last_input = None

    def filter_orders(self, orders):
        self.last_input = orders
        # simple rule: don't allow orders with quantity > 100
        out = [o for o in orders if o.get("quantity", 0) <= 100]
        return out


class DummyBracketManager:
    def __init__(self):
        self.registered = []

    def register_bracket(
        self, parent_order_id, symbol, side, qty, entry_price, bracket_cfg
    ):
        self.registered.append(
            {
                "parent": parent_order_id,
                "symbol": symbol,
                "side": side,
                "qty": qty,
                "entry_price": entry_price,
                "cfg": bracket_cfg,
            }
        )
        # simulate returning bracket id
        return f"br-{symbol}-{qty}"


class DummyOrchestrator:
    def __init__(self):
        self.bracket_manager = DummyBracketManager()
        self._prices = {"TCS": 100.0, "RELIANCE": 2000.0}

    def _get_last_price(self, symbol):
        return self._prices.get(symbol)


def test_register_and_list_strategies():
    pm = PortfolioManager()
    s = DummyStrategy("s1", [])
    pm.register_strategy(s)
    assert any(x["id"] == "s1" for x in pm.list_strategies())


def test_generate_and_net_orders_basic():
    s1 = DummyStrategy("s1", [{"symbol": "RELIANCE", "side": "buy", "quantity": 10}])
    s2 = DummyStrategy("s2", [{"symbol": "RELIANCE", "side": "buy", "quantity": 5}])
    pm = PortfolioManager()
    pm.register_strategy(s1)
    pm.register_strategy(s2)
    plan = pm.generate_portfolio_plan({})
    assert len(plan) == 1
    assert plan[0]["quantity"] == 15
    assert set(plan[0]["strategies"]) == {"s1", "s2"}


def test_conflicting_sides_stay_separate():
    s1 = DummyStrategy("s1", [{"symbol": "INFY", "side": "buy", "quantity": 10}])
    s2 = DummyStrategy("s2", [{"symbol": "INFY", "side": "sell", "quantity": 3}])
    pm = PortfolioManager()
    pm.register_strategy(s1)
    pm.register_strategy(s2)
    plan = pm.generate_portfolio_plan({})
    # both sides should be present
    assert any(p["side"] == "buy" and p["quantity"] == 10 for p in plan)
    assert any(p["side"] == "sell" and p["quantity"] == 3 for p in plan)


def test_risk_manager_filtering_and_global_caps():
    s1 = DummyStrategy(
        "s1", [{"symbol": "X", "side": "buy", "quantity": 500}], allocation=1.0
    )
    pm = PortfolioManager(risk_manager=DummyRiskManager())
    pm.register_strategy(s1)
    plan = pm.generate_portfolio_plan({})
    # DummyRiskManager filters >100
    assert all(p["quantity"] <= 100 for p in plan)


def test_per_strategy_and_global_symbol_caps_and_bracket_attach():
    # strategy requests 50 TCS with TP/SL
    ords = [
        {
            "symbol": "TCS",
            "side": "buy",
            "quantity": 50,
            "take_profit": 110.0,
            "stop_loss": 95.0,
            "price": 100.0,
        }
    ]
    s1 = DummyStrategy("s1", ords, allocation=1.0, per_symbol_cap=40)
    orch = DummyOrchestrator()
    pm = PortfolioManager(orchestrator=orch)
    pm.set_global_symbol_cap("TCS", 30)  # global cap tighter than strategy cap
    pm.register_strategy(s1)
    plan = pm.generate_portfolio_plan({})
    # global cap was 30 so final quantity should be <=30
    assert sum(p["quantity"] for p in plan if p["symbol"] == "TCS") <= 30
    # bracket manager should have been called (best-effort)
    assert len(orch.bracket_manager.registered) >= 1


def test_feedback_recording_and_strategy_hook():
    s1 = DummyStrategy("s1", [{"symbol": "TCS", "side": "buy", "quantity": 1}])
    pm = PortfolioManager()
    pm.register_strategy(s1)
    # simulate execution feedback
    pm.record_trade_result(
        {
            "strategy_id": "s1",
            "symbol": "TCS",
            "qty": 1,
            "price": 100.0,
            "pnl": 5.0,
            "win": True,
        }
    )
    metrics = pm.get_strategy_metrics("s1")
    assert metrics["trades"] == 1
    assert metrics["wins"] == 1
    assert metrics["pnl"] == 5.0
    # strategy received hook
    assert len(s1.received_feedback) == 1
