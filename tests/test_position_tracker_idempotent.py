# path: tests/test_position_tracker_idempotent.py

from qaai_system.portfolio.position_tracker import PositionTracker


def test_apply_fill_event_is_idempotent_on_trade_id():
    tracker = PositionTracker()

    event = {
        "trade_id": "TRADE-1",
        "symbol": "INFY",
        "side": "BUY",
        "filled_qty": 10,
        "avg_fill_price": 100.0,
    }

    # First application should open a position
    res1 = tracker.apply_fill_event(event)
    pos1 = tracker.get_position("INFY")
    assert pos1 is not None
    assert pos1.quantity == 10
    assert res1["realized_pnl"] == 0.0
    assert res1["position_closed"] is False

    # Second application with same trade_id should be a no-op
    res2 = tracker.apply_fill_event(event)
    pos2 = tracker.get_position("INFY")
    assert pos2 is not None
    assert pos2.quantity == 10  # unchanged
    assert res2["realized_pnl"] == 0.0
    assert res2["position_closed"] is False
