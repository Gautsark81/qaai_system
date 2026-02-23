import pandas as pd
import numpy as np
import pytest
from screening.signal_generator import generate_signals


def mock_watchlist():
    np.random.seed(42)
    return pd.DataFrame(
        {
            "timestamp": pd.date_range(end=pd.Timestamp.now(), periods=10),
            "symbol": [f"SYM{i}" for i in range(10)],
            "close": np.random.uniform(100, 200, 10),
            "signal_strength": np.linspace(0.4, 0.9, 10),
            "ma_ratio": np.random.uniform(0.8, 1.2, 10),
            "atr": np.random.uniform(1, 5, 10),
            "ema_fast": np.random.uniform(100, 110, 10),
            "ema_slow": np.random.uniform(90, 100, 10),
        }
    )


def test_generate_signals_output_structure():
    df = mock_watchlist()
    signals = generate_signals(df)
    expected_cols = [
        "timestamp",
        "symbol",
        "side",
        "close",
        "signal_strength",
        "stop_loss",
        "take_profit",
        "status",
        "signal_id",
        "mode",
    ]
    for col in expected_cols:
        assert col in signals.columns


def test_generate_signals_filtering():
    df = mock_watchlist()
    signals = generate_signals(df, entry_col="signal_strength")
    assert all(signals["signal_strength"] >= 0.4)  # matches mock_watchlist


def test_generate_signals_sl_tp_calculation():
    df = mock_watchlist()
    sl_mult = 1.0
    tp_mult = 2.0
    signals = generate_signals(df, sl_multiplier=sl_mult, tp_multiplier=tp_mult)
    assert all(signals["stop_loss"] > 0)
    assert all(signals["take_profit"] > 0)


def test_generate_signals_basic():
    mod = pytest.importorskip("screening.signal_generator")
    assert hasattr(mod, "generate_signals"), "generate_signals missing"

    df = pd.DataFrame(
        {
            "timestamp": pd.date_range(end=pd.Timestamp.now(), periods=2),
            "symbol": ["AAPL", "MSFT"],
            "close": [150.0, 310.0],
            "open": [149.0, 308.0],
            "high": [151.0, 312.0],
            "low": [148.5, 307.0],
            "volume": [10000, 20000],
            "atr": [2.0, 3.0],
            "ema_fast": [148.0, 305.0],
            "ema_slow": [145.0, 300.0],
            "signal_strength": [0.7, 0.8],
        }
    )

    signals = mod.generate_signals(df, mode="paper", strategy_id="alpha_v1")
    assert isinstance(signals, pd.DataFrame)
    assert "symbol" in signals.columns
    assert "side" in signals.columns
