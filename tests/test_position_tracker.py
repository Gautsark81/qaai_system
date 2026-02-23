# path: tests/test_position_tracker.py

import math

from qaai_system.portfolio.position_tracker import PositionTracker


class DummyLogger:
    def __init__(self):
        self.last_info = None

    def info(self, msg):
        self.last_info = msg

    def debug(self, msg, *args, **kwargs):
        # not needed for these tests, but harmless
        pass


def test_open_long_and_unrealized_pnl():
    prices = {"INFY": 120.0}
    tracker = PositionTracker(price_fetcher=lambda s: prices[s])

    # Open long 10 @ 100
    res = tracker.apply_fill(symbol="INFY", side="BUY", qty=10, price=100.0)
    assert res["symbol"] == "INFY"
    assert res["side"] == "LONG"
    assert res["realized_pnl"] == 0.0
    assert res["position_closed"] is False

    pos = tracker.get_position("INFY")
    assert pos is not None
    assert pos.quantity == 10
    assert pos.avg_price == 100.0

    snap = tracker.get_portfolio_snapshot()
    pos_snap = snap.positions["INFY"]
    # unrealized PnL = (120 - 100) * 10 = 200
    assert math.isclose(pos_snap["unrealized_pnl"], 200.0, rel_tol=1e-6)
    assert snap.num_open_positions == 1


def test_close_long_realized_pnl():
    tracker = PositionTracker()

    tracker.apply_fill("NIFTY", "BUY", 10, 100.0)
    # Close entire position with SELL 10 @ 110
    res = tracker.apply_fill("NIFTY", "SELL", 10, 110.0)

    assert res["symbol"] == "NIFTY"
    assert res["position_closed"] is True
    # realized PnL = (110 - 100) * 10 = 100
    assert math.isclose(res["realized_pnl"], 100.0, rel_tol=1e-6)

    pos = tracker.get_position("NIFTY")
    assert pos is None

    closed = tracker.get_closed_trades()
    assert len(closed) == 1
    trade = closed[0]
    assert trade["symbol"] == "NIFTY"
    assert math.isclose(trade["realized_pnl"], 100.0, rel_tol=1e-6)

    snap = tracker.get_portfolio_snapshot()
    assert snap.num_open_positions == 0
    assert math.isclose(snap.realized_pnl, 100.0, rel_tol=1e-6)


def test_partial_close_and_flip():
    tracker = PositionTracker()

    # Start long 10 @ 100
    tracker.apply_fill("SBIN", "BUY", 10, 100.0)
    # Partial close 5 @ 110 -> realized PnL = 5 * 10 = 50, still long 5
    res1 = tracker.apply_fill("SBIN", "SELL", 5, 110.0)
    assert res1["position_closed"] is False
    pos = tracker.get_position("SBIN")
    assert pos is not None
    assert pos.side == "LONG"
    assert pos.quantity == 5
    assert math.isclose(pos.realized_pnl, 50.0, rel_tol=1e-6)

    # Now SELL 10 @ 90:
    # - closes remaining 5 long: realized PnL delta = (90 - 100) * 5 = -50
    #   cumulative realized on that LONG becomes ~0
    # - opens new SHORT 5 @ 90
    res2 = tracker.apply_fill("SBIN", "SELL", 10, 90.0)
    assert res2["position_closed"] is False  # because we reopen on the opposite side

    pos2 = tracker.get_position("SBIN")
    assert pos2 is not None
    assert pos2.side == "SHORT"
    assert pos2.quantity == 5
    assert pos2.avg_price == 90.0

    # total realized PnL on the closed LONG should be approx 0
    snap = tracker.get_portfolio_snapshot()
    assert math.isclose(snap.realized_pnl, 0.0, abs_tol=1e-6)


def test_close_position_api_and_log_snapshot():
    logger = DummyLogger()
    prices = {"RELIANCE": 2500.0}
    tracker = PositionTracker(price_fetcher=lambda s: prices[s], logger=logger)

    tracker.apply_fill("RELIANCE", "BUY", 2, 2400.0)

    # Use close_position() API to close at current mark price (2500)
    res = tracker.close_position("RELIANCE", reason="MANUAL_EXIT")
    assert res is not None
    assert res["position_closed"] is True
    # realized PnL = (2500 - 2400) * 2 = 200
    assert math.isclose(res["realized_pnl"], 200.0, rel_tol=1e-6)

    assert tracker.get_position("RELIANCE") is None

    # Log snapshot and ensure logger got something
    tracker.log_snapshot(equity=1_00_000.0, cash=90_000.0)
    assert logger.last_info is not None
    assert logger.last_info.get("event") == "PORTFOLIO_SNAPSHOT"
    assert "positions" in logger.last_info
