# tests/test_feature_calc.py
import pandas as pd
import numpy as np
from modules.data_pipeline.features import compute_atr, compute_rsi, compute_rolling_features

def make_simple_ohlcv(n=30):
    idx = pd.date_range("2025-01-01", periods=n, freq="D")
    close = pd.Series(np.linspace(100, 110, n), index=idx)
    high = close + 0.5
    low = close - 0.5
    open_ = close.shift(1).fillna(close.iloc[0])
    volume = pd.Series(np.linspace(1000, 2000, n), index=idx)
    df = pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": volume})
    df.index.name = "timestamp"
    return df

def test_atr_basic():
    df = make_simple_ohlcv(20)
    atr = compute_atr(df, period=5)
    assert not atr.isna().all()
    # ATR should be positive
    assert (atr >= 0).all()

def test_rsi_basic():
    df = make_simple_ohlcv(20)
    rsi = compute_rsi(df, period=5)
    assert not rsi.isna().all()
    assert ((rsi >= 0) & (rsi <= 100)).all()

def test_compute_rolling_features_columns():
    df = make_simple_ohlcv(50)
    feats = compute_rolling_features(df, window_days=21)
    # expected feature columns exist
    for c in ["atr_14", "rsi_14", "ema_10", "ema_50", "realized_vol_21"]:
        assert c in feats.columns
    assert len(feats) == len(df)
