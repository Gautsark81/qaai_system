import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from modules.backtester.fill_models import bars_to_ticks, simulate_partial_fill, VolumetricImpact, FillResult


def make_sample_bars(num=6, start="2020-01-01T09:15:00", base_price=100.0):
    idx = pd.date_range(start, periods=num, freq="min")
    prices = base_price + np.arange(num) * 0.1
    df = pd.DataFrame({
        "open": prices,
        "high": prices * 1.001,
        "low": prices * 0.999,
        "close": prices,
        "volume": np.linspace(50, 200, num).astype(float),
    }, index=idx)
    return df


def test_bars_to_ticks_basic():
    bars = make_sample_bars()
    ticks = bars_to_ticks(bars, default_liquidity=100.0)
    # index preserved
    assert not ticks.empty
    assert "bid" in ticks.columns and "ask" in ticks.columns
    assert "bid_size" in ticks.columns and "ask_size" in ticks.columns
    assert (ticks["bid_size"] > 0).all()
    assert (ticks["ask_size"] > 0).all()


def test_simulate_partial_fill_basic_fill():
    bars = make_sample_bars(num=10, base_price=200.0)
    ticks = bars_to_ticks(bars, default_liquidity=50.0)
    # place a buy order for small qty that should fully fill
    order_qty = 10.0
    result = simulate_partial_fill(side="BUY", order_qty=order_qty, order_price=200.5, ticks=ticks, max_aggressive_fraction=1.0, min_fill_size=1.0)
    assert isinstance(result, FillResult)
    assert result.filled_quantity > 0
    assert result.filled_quantity <= order_qty + 1e-8
    assert result.avg_price > 0
    assert len(result.fills) >= 1
    # each fill qty > 0
    assert all(f.qty > 0 for f in result.fills)


def test_simulate_partial_fill_respects_liquidity_limit():
    bars = make_sample_bars(num=3, base_price=50.0)
    # very low liquidity -> cannot fill large order
    ticks = bars_to_ticks(bars, default_liquidity=1.0)
    order_qty = 1000.0
    result = simulate_partial_fill(side="BUY", order_qty=order_qty, order_price=50.0, ticks=ticks, max_aggressive_fraction=1.0, min_fill_size=1.0)
    # should not magically fill beyond available book
    assert result.filled_quantity <= (ticks["ask_size"].sum() + 1e-8)
    assert result.filled_quantity < order_qty


def test_volumetric_impact_monotonicity_buy():
    # For BUY side, larger executed_qty should increase price > smaller executed
    model = VolumetricImpact(base_pct=0.0001, sensitivity=1.0, exponent=0.5)
    base_price = 100.0
    small_price = model.apply("BUY", base_price, executed_qty=1.0, tick_liquidity=100.0)
    large_price = model.apply("BUY", base_price, executed_qty=50.0, tick_liquidity=100.0)
    assert large_price > small_price >= base_price


def test_volumetric_impact_monotonicity_sell():
    # For SELL side, larger executed_qty should decrease price < smaller executed
    model = VolumetricImpact(base_pct=0.0001, sensitivity=1.0, exponent=0.5)
    base_price = 200.0
    small_price = model.apply("SELL", base_price, executed_qty=1.0, tick_liquidity=100.0)
    large_price = model.apply("SELL", base_price, executed_qty=80.0, tick_liquidity=100.0)
    assert large_price < small_price <= base_price
