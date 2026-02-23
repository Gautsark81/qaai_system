from datetime import datetime

from modules.portfolio.state import PortfolioState
from modules.portfolio.state import Symbol, StrategyId


def test_open_position():
    state = PortfolioState(cash=100_000)

    state.apply_trade(
        symbol=Symbol("NIFTY"),
        quantity=10,
        price=100,
        strategy_id=StrategyId("trend"),
    )

    assert state.cash == 99_000
    assert "NIFTY" in state.positions
    assert state.positions["NIFTY"].avg_price == 100


def test_increase_position_weighted_price():
    state = PortfolioState(cash=100_000)

    state.apply_trade(symbol=Symbol("NIFTY"), quantity=10, price=100, strategy_id=StrategyId("s1"))
    state.apply_trade(symbol=Symbol("NIFTY"), quantity=10, price=110, strategy_id=StrategyId("s1"))

    pos = state.positions["NIFTY"]
    assert pos.quantity == 20
    assert round(pos.avg_price, 2) == 105.0


def test_close_position_realized_pnl():
    state = PortfolioState(cash=100_000)

    state.apply_trade(symbol=Symbol("NIFTY"), quantity=10, price=100, strategy_id=StrategyId("s1"))
    state.apply_trade(symbol=Symbol("NIFTY"), quantity=-10, price=120, strategy_id=StrategyId("s1"))

    assert "NIFTY" not in state.positions
    assert state.realized_pnl == 200
    assert state.cash == 100_200


def test_snapshot_metrics():
    state = PortfolioState(cash=50_000)
    state.apply_trade(symbol=Symbol("BANKNIFTY"), quantity=5, price=200, strategy_id=StrategyId("s2"))

    snap = state.snapshot(
        timestamp=datetime.utcnow(),
        prices={"BANKNIFTY": 210},
    )

    assert snap.metrics["unrealized_pnl"] == 50
    assert snap.metrics["equity"] == 50_000 - 1_000 + 50
