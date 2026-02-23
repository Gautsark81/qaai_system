# tests/test_position_manager.py
import pytest
from qaai_system.execution.position_manager import PositionManager


def test_fifo_basic_buy_sell_unrealized_realized():
    pm = PositionManager(method="fifo")

    # buy 100 @ 10
    r = pm.on_fill("A", "buy", 100, 10.0)
    assert pytest.approx(r, abs=1e-9) == 0.0

    # buy 50 @ 12
    r = pm.on_fill("A", "buy", 50, 12.0)
    assert pytest.approx(r, abs=1e-9) == 0.0

    # sell 120 @ 15 -> realized = (15-10)*100 + (15-12)*20 = 500 + 60 = 560
    r = pm.on_fill("A", "sell", 120, 15.0)
    assert pytest.approx(r, rel=1e-9) == 560.0

    pos = pm.get_position("A", market_price=15.0)
    assert pos["qty"] == 30
    # unrealized on remaining 30 bought at 12 => (15-12)*30 = 90
    assert pytest.approx(pos["unrealized_pnl"], rel=1e-9) == 90.0
    assert pytest.approx(pos["realized_pnl"], rel=1e-9) == 560.0


def test_avg_basic_behavior():
    pm = PositionManager(method="avg")
    # buy 100 @ 10
    pm.on_fill("B", "buy", 100, 10.0)
    # buy 100 @ 12 -> avg_cost = 11
    pm.on_fill("B", "buy", 100, 12.0)
    pos = pm.get_position("B", market_price=12.0)
    assert pos["qty"] == 200
    assert pytest.approx(pos["avg_cost"], rel=1e-9) == 11.0

    # sell 50 @ 15 -> realized = (15 - 11) * 50 = 200
    r = pm.on_fill("B", "sell", 50, 15.0)
    assert pytest.approx(r, rel=1e-9) == 200.0
    pos2 = pm.get_position("B", market_price=15.0)
    assert pos2["qty"] == 150
    assert pytest.approx(pos2["realized_pnl"], rel=1e-9) == 200.0
