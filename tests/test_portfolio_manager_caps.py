from qaai_system.execution.portfolio_manager import PortfolioManager
from tests.conftest import DummyStrategy


def make_order(symbol="AAA", side="buy", qty=100, price=10.0):
    return {"symbol": symbol, "side": side, "quantity": qty, "price": price}


def test_global_symbol_cap_applies():
    pm = PortfolioManager()
    pm.set_global_symbol_cap("AAA", 5)

    strat = DummyStrategy("s1", [make_order(symbol="AAA", qty=10)])
    pm.register_strategy(strat)

    plan = pm.generate_portfolio_plan({}, account_equity=1000)
    assert plan[0]["quantity"] <= 5  # capped


def test_per_strategy_cap_applies():
    class StratWithCap(DummyStrategy):
        def __init__(self, sid, orders, cap):
            super().__init__(sid, orders)
            self.per_symbol_cap = cap

    pm = PortfolioManager()
    strat = StratWithCap("s1", [make_order(qty=20)], cap=7)
    pm.register_strategy(strat)

    plan = pm.generate_portfolio_plan({}, account_equity=1000)
    assert plan[0]["quantity"] <= 7


def test_allocation_scaling_applies():
    class StratWithAlloc(DummyStrategy):
        def __init__(self, sid, orders, alloc):
            super().__init__(sid, orders)
            self.allocation = alloc

    pm = PortfolioManager()
    strat = StratWithAlloc("s1", [make_order(qty=10)], alloc=0.25)
    pm.register_strategy(strat)

    plan = pm.generate_portfolio_plan({}, account_equity=1000)
    # 10 * 0.25 = 2.5 → floored to 2
    assert plan[0]["quantity"] == 2


def test_global_exposure_cap_scales_orders():
    pm = PortfolioManager(global_exposure_cap=0.1)  # 10% of equity
    strat = DummyStrategy("s1", [make_order(qty=100, price=10.0)])  # exposure = 1000
    pm.register_strategy(strat)

    plan = pm.generate_portfolio_plan({}, account_equity=1000)  # cap = 100
    assert plan[0]["quantity"] < 100  # scaled down
