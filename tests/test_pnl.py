# tests/test_pnl.py
from backtest.pnl import PnLCalculator


def test_pnl_records_realized_and_unrealized():
    pnl = PnLCalculator()
    # Simulate buy fill
    order_buy = {"symbol": "AAA", "side": "buy", "quantity": 10, "price": 5.0}
    fill_buy = {"order_id": "o1", "status": "filled", "price": 5.0}
    pnl.record_fill(fill_buy, order_buy)
    # After buy, unrealized with higher market price should be positive
    market = {"AAA": 6.0}
    summary = pnl.summary(market)
    assert summary["positions"]["AAA"]["qty"] == 10
    assert summary["unrealized"] == (6.0 - 5.0) * 10
    # Now sell some to realize PnL
    order_sell = {"symbol": "AAA", "side": "sell", "quantity": 5, "price": 7.0}
    fill_sell = {"order_id": "o2", "status": "filled", "price": 7.0}
    pnl.record_fill(fill_sell, order_sell)
    s2 = pnl.summary({"AAA": 7.0})
    # realized should be (7-5)*5 = 10
    assert abs(s2["realized"] - 10.0) < 1e-9
    # remaining qty should be 5
    assert s2["positions"]["AAA"]["qty"] == 5


def test_pnl_handles_zero_positions():
    pnl = PnLCalculator()
    # No positions -> unrealized 0
    assert pnl.summary({})["unrealized"] == 0
