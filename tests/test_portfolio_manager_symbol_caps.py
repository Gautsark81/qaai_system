from qaai_system.execution.portfolio_manager import PortfolioManager
from tests.conftest import DummyStrategy


def make_order(symbol="AAA", side="buy", qty=10, price=10.0):
    return {"symbol": symbol, "side": side, "quantity": qty, "price": price}


def test_single_symbol_cap_trims_orders_proportionally():
    pm = PortfolioManager()
    pm.set_global_symbol_cap("AAA", 6)

    strat1 = DummyStrategy("s1", [make_order(symbol="AAA", qty=10)])
    strat2 = DummyStrategy("s2", [make_order(symbol="AAA", qty=20)])
    pm.register_strategy(strat1)
    pm.register_strategy(strat2)

    plan = pm.generate_portfolio_plan({}, account_equity=1000)

    # Two orders collapsed into one netted order
    assert len(plan) == 1
    o = plan[0]
    assert o["symbol"] == "AAA"
    # Quantity should be capped at or below 6
    assert o["quantity"] <= 6


def test_multiple_symbols_only_capped_one():
    pm = PortfolioManager()
    pm.set_global_symbol_cap("AAA", 5)  # only AAA capped

    strat = DummyStrategy(
        "s1",
        [
            make_order(symbol="AAA", qty=10),
            make_order(symbol="BBB", qty=20),
        ],
    )
    pm.register_strategy(strat)

    plan = pm.generate_portfolio_plan({}, account_equity=1000)

    # AAA should be capped, BBB unchanged
    qa = [o for o in plan if o["symbol"] == "AAA"][0]
    qb = [o for o in plan if o["symbol"] == "BBB"][0]

    assert qa["quantity"] <= 5
    assert qb["quantity"] == 20


def test_no_cap_means_no_trimming():
    pm = PortfolioManager()

    strat = DummyStrategy("s1", [make_order(symbol="AAA", qty=15)])
    pm.register_strategy(strat)

    plan = pm.generate_portfolio_plan({}, account_equity=1000)

    assert plan[0]["quantity"] == 15  # unchanged


def test_cap_lower_than_total_splits_fairly():
    pm = PortfolioManager()
    pm.set_global_symbol_cap("AAA", 3)

    strat = DummyStrategy(
        "s1",
        [
            make_order(symbol="AAA", qty=5),
            make_order(symbol="AAA", qty=7),
        ],
    )
    pm.register_strategy(strat)

    plan = pm.generate_portfolio_plan({}, account_equity=1000)

    # Netted into one AAA order capped at 3
    assert len(plan) == 1
    assert plan[0]["symbol"] == "AAA"
    assert plan[0]["quantity"] <= 3


def test_caps_apply_separately_to_buys_and_sells():
    pm = PortfolioManager()
    pm.set_global_symbol_cap("AAA", 5)

    strat = DummyStrategy(
        "s1",
        [
            make_order(symbol="AAA", side="buy", qty=10),
            make_order(symbol="AAA", side="sell", qty=12),
        ],
    )
    pm.register_strategy(strat)

    plan = pm.generate_portfolio_plan({}, account_equity=1000)

    # Expect two separate orders (buy + sell), both capped
    buys = [o for o in plan if o["symbol"] == "AAA" and o["side"] == "buy"]
    sells = [o for o in plan if o["symbol"] == "AAA" and o["side"] == "sell"]

    assert len(buys) == 1
    assert len(sells) == 1
    assert buys[0]["quantity"] <= 5
    assert sells[0]["quantity"] <= 5


def test_caps_independent_for_buys_and_sells():
    pm = PortfolioManager()
    pm.set_global_symbol_cap("AAA", 8)

    strat = DummyStrategy(
        "s1",
        [
            make_order(symbol="AAA", side="buy", qty=5),  # under cap, unchanged
            make_order(
                symbol="AAA", side="sell", qty=20
            ),  # over cap, should be trimmed
        ],
    )
    pm.register_strategy(strat)

    plan = pm.generate_portfolio_plan({}, account_equity=1000)

    buys = [o for o in plan if o["symbol"] == "AAA" and o["side"] == "buy"]
    sells = [o for o in plan if o["symbol"] == "AAA" and o["side"] == "sell"]

    # Buy stays as-is
    assert buys and buys[0]["quantity"] == 5
    # Sell capped down to <= 8
    assert sells and sells[0]["quantity"] <= 8
