from qaai_system.execution.portfolio_manager import PortfolioManager
from tests.conftest import DummyStrategy, make_order


def test_exposure_below_cap_no_scaling():
    pm = PortfolioManager(global_exposure_cap=0.5)  # 50% cap
    strat = DummyStrategy("s1", [make_order(qty=10, price=10)])  # exposure = 100
    pm.register_strategy(strat)

    plan = pm.generate_portfolio_plan({}, account_equity=1000)  # cap = 500
    assert plan[0]["quantity"] == 10  # no scaling needed


def test_exposure_equal_to_cap_no_scaling():
    pm = PortfolioManager(global_exposure_cap=0.1)  # 10% cap
    strat = DummyStrategy("s1", [make_order(qty=10, price=10)])  # exposure = 100
    pm.register_strategy(strat)

    plan = pm.generate_portfolio_plan({}, account_equity=1000)  # cap = 100
    assert plan[0]["quantity"] == 10  # exactly at cap


def test_exposure_above_cap_scales_down():
    pm = PortfolioManager(global_exposure_cap=0.1)  # 10% cap
    strat = DummyStrategy("s1", [make_order(qty=100, price=10)])  # exposure = 1000
    pm.register_strategy(strat)

    plan = pm.generate_portfolio_plan({}, account_equity=1000)  # cap = 100
    assert plan[0]["quantity"] < 100  # should scale down
    assert plan[0]["quantity"] > 0  # should not vanish completely


def test_multiple_orders_scaled_proportionally():
    pm = PortfolioManager(global_exposure_cap=0.2)  # 20% cap
    strat = DummyStrategy(
        "s1",
        [
            make_order(symbol="AAA", qty=50, price=10),  # exposure = 500
            make_order(symbol="BBB", qty=20, price=20),  # exposure = 400
        ],
    )  # total = 900
    pm.register_strategy(strat)

    plan = pm.generate_portfolio_plan({}, account_equity=1000)  # cap = 200
    total_exposure = sum(o["quantity"] * o["price"] for o in plan)

    assert total_exposure <= 200 + 1e-6  # within cap
    assert all(o["quantity"] > 0 for o in plan)  # each order survives


def test_zero_equity_skips_scaling():
    pm = PortfolioManager(global_exposure_cap=0.1)
    strat = DummyStrategy("s1", [make_order(qty=50, price=10)])
    pm.register_strategy(strat)

    plan = pm.generate_portfolio_plan({}, account_equity=0)  # no equity info
    assert plan[0]["quantity"] == 50  # unchanged


def test_no_equity_param_skips_scaling():
    pm = PortfolioManager(global_exposure_cap=0.1)
    strat = DummyStrategy("s1", [make_order(qty=50, price=10)])
    pm.register_strategy(strat)

    plan = pm.generate_portfolio_plan({}, account_equity=None)  # no equity passed
    assert plan[0]["quantity"] == 50  # unchanged


def test_price_survives_netting():
    """Regression test: ensure price is preserved after netting identical orders."""
    pm = PortfolioManager()

    orders = [
        {"symbol": "AAA", "side": "buy", "quantity": 5, "price": 10.0},
        {"symbol": "AAA", "side": "buy", "quantity": 5, "price": 10.0},
    ]

    # Apply netting directly
    netted = pm._net_orders(orders)

    assert len(netted) == 1
    assert netted[0]["quantity"] == 10  # summed
    assert netted[0]["price"] == 10.0  # 🔹 price preserved


def test_exposure_with_zero_equity_and_cap_drops_orders():
    """If equity is 0 and global_exposure_cap > 0, orders should vanish (exposure = 0 cap)."""
    pm = PortfolioManager(global_exposure_cap=0.1)
    strat_orders = [{"symbol": "AAA", "side": "buy", "quantity": 10, "price": 10.0}]
    pm.register_strategy(
        type("S", (), {"id": "s1", "generate_orders": lambda self, _: strat_orders})()
    )

    plan = pm.generate_portfolio_plan({}, account_equity=0)  # equity=0 → cap=0
    assert all(o["quantity"] == 0 for o in plan)


def test_qty_preserved_when_quantity_missing():
    """Regression: ensure 'qty' is mapped into 'quantity' correctly."""
    pm = PortfolioManager()
    strat = DummyStrategy(
        "s1", [{"symbol": "XYZ", "side": "buy", "qty": 15, "price": 20.0}]
    )
    pm.register_strategy(strat)

    plan = pm.generate_portfolio_plan({}, account_equity=1000)
    assert plan[0]["quantity"] == 15
    assert plan[0]["price"] == 20.0
    assert plan[0]["symbol"] == "XYZ"
    assert plan[0]["side"] == "buy"


def test_missing_qty_and_quantity_defaults_to_zero():
    """Regression: if both 'qty' and 'quantity' are missing, it should default to 0."""
    pm = PortfolioManager()
    strat = DummyStrategy(
        "s1", [{"symbol": "XYZ", "side": "buy", "price": 20.0}]
    )  # no qty/quantity
    pm.register_strategy(strat)

    plan = pm.generate_portfolio_plan({}, account_equity=1000)
    assert plan[0]["quantity"] == 0
    assert plan[0]["price"] == 20.0
    assert plan[0]["symbol"] == "XYZ"
    assert plan[0]["side"] == "buy"
