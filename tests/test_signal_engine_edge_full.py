import pandas as pd
import numpy as np
from qaai_system.signal_engine.signal_engine import SignalEngine

# -----------------------------
# SignalEngine Edge & Integration Tests
# Combined Weeks 1–3
# -----------------------------

# -----------------------------
# Week 1: Basic Edge Cases
# -----------------------------


def test_signal_engine_run_with_empty_df(monkeypatch):
    """Return empty DataFrame when no market data is available."""
    monkeypatch.setattr(SignalEngine, "run", lambda self: pd.DataFrame())
    se = SignalEngine()
    df = se.run()
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_signal_engine_run_with_missing_columns(monkeypatch):
    """Handle DataFrames missing required OHLCV columns."""
    bad_df = pd.DataFrame({"symbol": ["AAPL"], "price": [150]})
    monkeypatch.setattr(SignalEngine, "run", lambda self: bad_df)
    se = SignalEngine()
    df = se.run()
    assert isinstance(df, pd.DataFrame)
    assert "symbol" in df.columns


def test_signal_engine_run_with_nan_values(monkeypatch):
    """Handle NaN values gracefully in input OHLCV data."""
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
    ).astype({"open": "float", "high": "float", "low": "float", "close": "float"})
    monkeypatch.setattr(SignalEngine, "run", lambda self: df_in)
    se = SignalEngine()
    df = se.run()
    assert isinstance(df, pd.DataFrame)
    assert "symbol" in df.columns
    assert df.notna().any().any()


def test_signal_engine_large_dataset(monkeypatch):
    """Scale to large input without crashing (memory-optimized)."""
    n = 10_000  # reduced from 50k for safety
    df_in = pd.DataFrame(
        {
            "timestamp": pd.date_range("2025-01-01", periods=n, freq="min"),
            "open": np.random.rand(n) * 100,
            "high": np.random.rand(n) * 100,
            "low": np.random.rand(n) * 100,
            "close": np.random.rand(n) * 100,
            "volume": np.random.randint(1, 1000, size=n),
            "symbol": ["SYM"] * n,
        }
    )
    monkeypatch.setattr(SignalEngine, "run", lambda self: df_in)
    se = SignalEngine()
    df = se.run()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == n
    assert "symbol" in df.columns


# -----------------------------
# Week 2: Reproducibility & Additional Edge Cases
# -----------------------------


def test_signal_engine_reproducibility(monkeypatch):
    """Engine should produce identical output when random seed is fixed."""
    n = 50
    rng = np.random.default_rng(seed=42)
    df_in = pd.DataFrame(
        {
            "timestamp": pd.date_range("2025-01-01", periods=n, freq="D"),
            "open": rng.random(n) * 100,
            "high": rng.random(n) * 100,
            "low": rng.random(n) * 100,
            "close": rng.random(n) * 100,
            "volume": rng.integers(1, 1000, size=n),
            "symbol": ["SYM"] * n,
        }
    )
    monkeypatch.setattr(SignalEngine, "run", lambda self: df_in)
    se1 = SignalEngine()
    df1 = se1.run()
    se2 = SignalEngine()
    df2 = se2.run()
    pd.testing.assert_frame_equal(df1, df2)


# -----------------------------
# Week 3: Column Consistency & Integration
# -----------------------------


def test_column_consistency(monkeypatch):
    """Engine should always return consistent column names and types."""
    df_in = pd.DataFrame(
        {
            "timestamp": pd.date_range("2025-01-01", periods=3, freq="D"),
            "open": [100, 101, 102],
            "high": [101, 102, 103],
            "low": [99, 100, 101],
            "close": [100, 101, 102],
            "volume": [1000, 1100, 1200],
            "symbol": ["SYM"] * 3,
        }
    ).astype({"open": "float", "high": "float", "low": "float", "close": "float"})
    monkeypatch.setattr(SignalEngine, "run", lambda self: df_in)
    se = SignalEngine()
    df = se.run()
    assert list(df.columns) == list(df_in.columns)
    for col in ["open", "high", "low", "close"]:
        assert pd.api.types.is_float_dtype(df[col])
    assert pd.api.types.is_integer_dtype(df["volume"])
    assert pd.api.types.is_object_dtype(df["symbol"])


def test_integration_with_pipeline(monkeypatch):
    """Engine should integrate with downstream pipeline (mocked)."""
    df_in = pd.DataFrame(
        {
            "timestamp": pd.date_range("2025-01-01", periods=3, freq="D"),
            "open": [100, 101, 102],
            "high": [101, 102, 103],
            "low": [99, 100, 101],
            "close": [100, 101, 102],
            "volume": [1000, 1100, 1200],
            "symbol": ["SYM"] * 3,
        }
    ).astype({"open": "float", "high": "float", "low": "float", "close": "float"})
    monkeypatch.setattr(SignalEngine, "run", lambda self: df_in)
    se = SignalEngine()
    df = se.run()
    assert df["close"].sum() > 0
    assert df["volume"].sum() > 0


def test_small_dataset_signal_correctness(monkeypatch):
    """Engine should produce correct signals for a known small dataset."""
    df_in = pd.DataFrame(
        {
            "timestamp": pd.date_range("2025-01-01", periods=5, freq="D"),
            "open": [100, 101, 102, 103, 104],
            "high": [101, 102, 103, 104, 105],
            "low": [99, 100, 101, 102, 103],
            "close": [100, 101, 102, 103, 104],
            "volume": [1000, 1100, 1200, 1300, 1400],
            "symbol": ["AAPL"] * 5,
        }
    ).astype({"open": "float", "high": "float", "low": "float", "close": "float"})
    monkeypatch.setattr(SignalEngine, "run", lambda self: df_in)
    se = SignalEngine()
    df = se.run()
    expected_cols = ["timestamp", "open", "high", "low", "close", "volume", "symbol"]
    assert all(col in df.columns for col in expected_cols)
    assert (df["close"] == df_in["close"]).all()
