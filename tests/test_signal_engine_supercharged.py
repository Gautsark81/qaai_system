# tests/test_signal_engine_supercharged.py

import sys
import os
import pytest
import pandas as pd
import numpy as np

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qaai_system.signal_engine.signal_engine_supercharged import (
    SignalEngineSupercharged,
)


@pytest.fixture
def long_sample_df():
    """Create a realistic dataframe with enough rows to initialize all indicators."""
    n = 100  # enough rows for SMA/EMA/ATR/etc.
    dates = pd.date_range("2025-01-01", periods=n, freq="D")
    prices = np.linspace(100, 150, n) + np.random.normal(0, 1, n)
    high = prices + np.random.uniform(0.5, 1.5, n)
    low = prices - np.random.uniform(0.5, 1.5, n)
    open_ = prices + np.random.uniform(-1, 1, n)
    close = prices
    volume = np.random.randint(1000, 2000, n)
    symbol = ["SYM"] * n

    df = pd.DataFrame(
        {
            "timestamp": dates,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
            "symbol": symbol,
        }
    )
    return df


def test_supertrend_output(long_sample_df):
    """Supertrend should compute valid -1/1 signals without returning all NaN."""
    st = SignalEngineSupercharged.supertrend(long_sample_df)
    st_clean = st.dropna()
    assert len(st_clean) > 0
    assert set(np.unique(st_clean)).issubset({-1, 1})


def test_indicators(long_sample_df):
    """Test SMA, EMA, RSI, MACD, OBV, Bollinger Bands."""
    se = SignalEngineSupercharged()

    # SMA / EMA
    sma = se.sma(long_sample_df["close"], 5)
    ema = se.ema(long_sample_df["close"], 5)
    assert not sma.isna().all()
    assert not ema.isna().all()

    # RSI
    rsi = se.rsi(long_sample_df["close"], 14)
    assert not rsi.isna().all()

    # MACD
    macd, signal = se.macd(long_sample_df["close"])
    assert len(macd) == len(long_sample_df)
    assert len(signal) == len(long_sample_df)

    # OBV
    obv = se.obv(long_sample_df)
    assert len(obv) == len(long_sample_df)

    # Bollinger Bands
    upper, lower, width = se.bollinger_bands(long_sample_df["close"], 20)
    assert len(upper) == len(long_sample_df)
    assert len(lower) == len(long_sample_df)
    assert len(width) == len(long_sample_df)


def test_transform_for_ml(long_sample_df):
    """Ensure transform_for_ml produces correct output formats."""
    se = SignalEngineSupercharged()
    df = long_sample_df.copy()

    # Pandas output
    out_df = se.transform_for_ml(df, as_tensor=False)
    assert isinstance(out_df, pd.DataFrame)
    assert not out_df.empty

    # Torch tensor output
    try:
        import torch
    except Exception:
        import pytest
        pytest.skip("Torch not available in this environment")

        out_tensor = se.transform_for_ml(df, as_tensor=True)
        assert isinstance(out_tensor, torch.Tensor)
        assert out_tensor.shape[0] == len(df)
    except ImportError:
        pass  # skip torch test if not installed
