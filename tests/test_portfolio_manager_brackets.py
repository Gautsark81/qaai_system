from qaai_system.execution.portfolio_manager import PortfolioManager
from tests.conftest import DummyStrategy


class DummyBracketManager:
    def __init__(self):
        self.registered = []

    def register_bracket(
        self, parent_order_id, symbol, side, qty, entry_price, bracket_cfg
    ):
        self.registered.append(
            {
                "parent_order_id": parent_order_id,
                "symbol": symbol,
                "side": side,
                "qty": qty,
                "entry_price": entry_price,
                "bracket_cfg": bracket_cfg,
            }
        )


class DummyOrchestrator:
    def __init__(self):
        self.bracket_manager = DummyBracketManager()
        self._last_price = 123.0

    def _get_last_price(self, symbol):
        return self._last_price


def make_order(**overrides):
    base = {"symbol": "AAA", "side": "buy", "quantity": 10, "price": 100.0}
    base.update(overrides)
    return base


def test_bracket_attached_for_take_profit_and_stop_loss():
    orch = DummyOrchestrator()
    pm = PortfolioManager(orchestrator=orch)

    strat = DummyStrategy("s1", [make_order(take_profit=120.0, stop_loss=90.0)])
    pm.register_strategy(strat)

    plan = pm.generate_portfolio_plan({}, account_equity=1000)

    # Bracket should have been registered
    assert orch.bracket_manager.registered
    reg = orch.bracket_manager.registered[0]
    assert reg["symbol"] == "AAA"
    assert "take_profits" in reg["bracket_cfg"]
    assert "stop" in reg["bracket_cfg"]


def test_bracket_attached_for_trailing_stop():
    orch = DummyOrchestrator()
    pm = PortfolioManager(orchestrator=orch)

    strat = DummyStrategy("s1", [make_order(trailing_pct=0.1)])
    pm.register_strategy(strat)

    plan = pm.generate_portfolio_plan({}, account_equity=1000)

    assert orch.bracket_manager.registered
    cfg = orch.bracket_manager.registered[0]["bracket_cfg"]
    assert "trail" in cfg
    assert cfg["trail"]["type"] == "percent"


def test_no_bracket_if_no_tp_sl_trail():
    orch = DummyOrchestrator()
    pm = PortfolioManager(orchestrator=orch)

    strat = DummyStrategy("s1", [make_order()])  # no tp/sl/trail
    pm.register_strategy(strat)

    plan = pm.generate_portfolio_plan({}, account_equity=1000)

    assert orch.bracket_manager.registered == []


def test_bracket_manager_failure_is_logged(caplog):
    class FailingBracketManager(DummyBracketManager):
        def register_bracket(self, *a, **kw):
            raise RuntimeError("fail!")

    orch = DummyOrchestrator()
    orch.bracket_manager = FailingBracketManager()
    pm = PortfolioManager(orchestrator=orch)

    strat = DummyStrategy("s1", [make_order(take_profit=120.0)])
    pm.register_strategy(strat)

    with caplog.at_level("ERROR"):
        plan = pm.generate_portfolio_plan({}, account_equity=1000)

    # Should log the failure, but not crash
    assert "Failed to attach bracket" in caplog.text
