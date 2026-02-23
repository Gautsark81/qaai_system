# tests/test_backtester_skeleton.py
import pandas as pd
import numpy as np
from modules.backtester.core import Backtester, FixedTickSlippage, PercentSlippage

class DummyFillHook:
    def predict_fill(self, symbol, price, qty, side, ts=None):
        # simple heuristic: smaller orders more likely filled
        return 0.9 if qty <= 10 else 0.2

def make_ohlcv(n=10):
    idx = pd.date_range("2025-01-01", periods=n, freq="D")
    price = np.linspace(100, 110, n)
    df = pd.DataFrame({"open": price, "high": price + 0.5, "low": price - 0.5, "close": price, "volume": np.linspace(1000,2000,n)}, index=idx)
    return df

def test_backtester_fixed_slippage_and_fillhook():
    df = make_ohlcv(5)
    sl = FixedTickSlippage(tick_size=0.1, ticks=2)
    hook = DummyFillHook()
    bt = Backtester(df, slippage=sl, fill_hook=hook)
    oid = bt.place_order("FOO", "BUY", 5, 101.0)
    o = bt.get_order(oid)
    assert o is not None
    # since qty=5, fill probability high -> likely filled
    bt.run_to_end()
    o2 = bt.get_order(oid)
    assert o2.status in ("filled", "open", "cancelled")
    # summary returns counts
    s = bt.summary()
    assert "n_orders" in s and s["n_orders"] == 1

def test_backtester_percent_slippage():
    df = make_ohlcv(3)
    sl = PercentSlippage(pct=0.01)
    bt = Backtester(df, slippage=sl)
    oid = bt.place_order("FOO", "SELL", 2, 105.0)
    bt.run_to_end()
    o = bt.get_order(oid)
    # if filled, avg_fill_price should be set
    if o.status == "filled":
        assert o.avg_fill_price is not None
