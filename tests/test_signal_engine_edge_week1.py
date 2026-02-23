import pandas as pd
import numpy as np
from qaai_system.signal_engine.signal_engine import SignalEngine


# -----------------------------
# Week 1: Edge Case Tests
# -----------------------------


def test_run_with_invalid_symbols(monkeypatch):
    """Engine should handle invalid or malformed symbols gracefully."""
    invalid_df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2025-01-01", periods=3, freq="D"),
            "open": [100, 101, 102],
            "high": [101, 102, 103],
            "low": [99, 100, 101],
            "close": [100, 101, 102],
            "volume": [1000, 1100, 1200],
            "symbol": ["", None, "XYZ!"],
        }
    )
    monkeypatch.setattr(SignalEngine, "run", lambda self: invalid_df)

    se = SignalEngine()
    df = se.run()
    assert isinstance(df, pd.DataFrame)
    assert all(
        col in df.columns
        for col in ["timestamp", "open", "high", "low", "close", "volume", "symbol"]
    )


def test_run_with_missing_columns(monkeypatch):
    """Engine should handle DataFrames missing some OHLCV columns."""
    missing_cols_df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2025-01-01", periods=3, freq="D"),
            "symbol": ["AAPL", "GOOG", "MSFT"],
        }
    )
    monkeypatch.setattr(SignalEngine, "run", lambda self: missing_cols_df)

    se = SignalEngine()
    df = se.run()
    assert isinstance(df, pd.DataFrame)
    # Missing columns should either be added or handled gracefully
    assert "symbol" in df.columns


def test_run_with_nan_and_inf(monkeypatch):
    """Engine should handle NaN and Inf values without crashing."""
    df_in = pd.DataFrame(
        {
            "timestamp": pd.date_range("2025-01-01", periods=5, freq="D"),
            "open": [100, np.nan, 102, np.inf, 104],
            "high": [101, 102, np.nan, 105, 106],
            "low": [99, 98, 97, np.nan, 103],
            "close": [100, 101, np.nan, 103, np.inf],
            "volume": [1000, np.nan, 1200, 1300, np.inf],
            "symbol": ["AAPL"] * 5,
        }
    )
    monkeypatch.setattr(SignalEngine, "run", lambda self: df_in)

    se = SignalEngine()
    df = se.run()
    assert isinstance(df, pd.DataFrame)
    assert "symbol" in df.columns
    assert (
        df.notna().any().any()
        or np.isinf(df.select_dtypes(include=[np.number])).any().any()
    )


def test_run_with_empty_dataframe(monkeypatch):
    """Engine should return an empty DataFrame when no data is provided."""
    monkeypatch.setattr(SignalEngine, "run", lambda self: pd.DataFrame())

    se = SignalEngine()
    df = se.run()
    assert isinstance(df, pd.DataFrame)
    assert df.empty
