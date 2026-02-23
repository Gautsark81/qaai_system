# tests/test_volumetric_slippage.py
import pytest
from modules.backtester.volumetric_slippage import VolumetricSlippage, Order

def make_bar(volume=1000, close=100.0):
    return {"open": close, "high": close+1, "low": close-1, "close": close, "volume": volume}

def test_fill_partial_across_multiple_bars():
    vol_model = VolumetricSlippage(participation_rate=0.2, max_slice_fraction=0.5, impact_per_unit=0.0)
    order = Order(order_id="o1", symbol="X", side="BUY", qty=300.0, price=100.0)

    # First bar: capacity = 0.2 * 1000 = 200 -> fills 200
    filled1, price1, status1 = vol_model.fill(order, make_bar(volume=1000), remaining_qty=order.qty)
    assert pytest.approx(filled1, rel=1e-6) == 200.0
    assert status1 == "partial"

    # Remaining 100; second bar with small volume only 400 -> capacity 80, partial again
    filled2, price2, status2 = vol_model.fill(order, make_bar(volume=400), remaining_qty=order.qty - filled1)
    assert pytest.approx(filled2, rel=1e-6) == pytest.approx(80.0, rel=1e-6)
    assert status2 == "partial"

    # Third bar big enough to finish
    filled3, price3, status3 = vol_model.fill(order, make_bar(volume=1000), remaining_qty=order.qty - filled1 - filled2)
    assert pytest.approx(filled3 + filled1 + filled2, rel=1e-6) == pytest.approx(order.qty, rel=1e-6)
    assert status3 == "filled"

def test_zero_volume_open():
    vol_model = VolumetricSlippage()
    order = Order(order_id="o2", symbol="Y", side="SELL", qty=50.0, price=10.0)
    filled, price, status = vol_model.fill(order, {"close":10.0, "volume":0})
    assert filled == 0.0
    assert status == "open"
