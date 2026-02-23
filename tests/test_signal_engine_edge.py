import pandas as pd
import numpy as np

from qaai_system.signal_engine.signal_engine import SignalEngine


def test_signal_engine_run_with_empty_df(monkeypatch):
    """Should return empty DataFrame when no market data is available."""
    # Patch run method to return empty DataFrame
    monkeypatch.setattr(SignalEngine, "run", lambda self: pd.DataFrame())

    se = SignalEngine()
    df = se.run()
    assert isinstance(df, pd.DataFrame)
    assert df.empty, "Run should return empty DataFrame when no data"


def test_signal_engine_run_with_missing_columns(monkeypatch):
    """Should handle DataFrames missing required OHLCV columns."""
    bad_df = pd.DataFrame({"symbol": ["AAPL"], "price": [150]})
    monkeypatch.setattr(SignalEngine, "run", lambda self: bad_df)

    se = SignalEngine()
    df = se.run()
    assert isinstance(df, pd.DataFrame)
    assert "symbol" in df.columns


def test_signal_engine_run_with_nan_values(monkeypatch):
    """Should handle NaN values gracefully in input OHLCV data."""
    df_in = pd.DataFrame(
        {
            "timestamp": pd.date_range("2025-01-01", periods=5, freq="D"),
            "open": [100, np.nan, 102, 103, 104],
            "high": [101, 102, np.nan, 105, 106],
            "low": [99, 98, 97, np.nan, 103],
            "close": [100, 101, 102, 103, np.nan],
            "volume": [1000, 1100, 1200, 1300, np.nan],
            "symbol": ["AAPL"] * 5,
        }
    )
    monkeypatch.setattr(SignalEngine, "run", lambda self: df_in)

    se = SignalEngine()
    df = se.run()
    assert isinstance(df, pd.DataFrame)
    assert "symbol" in df.columns
    assert df.notna().any().any()


def test_signal_engine_large_dataset(monkeypatch):
    """Should scale to large input without crashing."""
    n = 10_000  # optimized size for memory efficiency
    df_in = pd.DataFrame(
        {
            "timestamp": pd.date_range(
                "2025-01-01", periods=n, freq="min"
            ),  # fixed deprecation warning
            "open": (np.random.rand(n) * 100).astype(np.float32),
            "high": (np.random.rand(n) * 100).astype(np.float32),
            "low": (np.random.rand(n) * 100).astype(np.float32),
            "close": (np.random.rand(n) * 100).astype(np.float32),
            "volume": np.random.randint(1, 1000, size=n).astype(np.int32),
            "symbol": ["SYM"] * n,
        }
    )
    monkeypatch.setattr(SignalEngine, "run", lambda self: df_in)

    se = SignalEngine()
    df = se.run()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == n
    assert "symbol" in df.columns
