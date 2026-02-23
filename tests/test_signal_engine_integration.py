import pandas as pd
import numpy as np
import pytest
from qaai_system.signal_engine.signal_engine import SignalEngine

# -----------------------------
# Reproducibility Tests
# -----------------------------


@pytest.mark.parametrize("seed", [42, 123, 999])
def test_signal_engine_reproducibility(monkeypatch, seed):
    """SignalEngine should produce consistent output for the same random seed."""
    np.random.seed(seed)

    # Create a random dataset
    df_in = pd.DataFrame(
        {
            "timestamp": pd.date_range("2025-01-01", periods=5),
            "open": np.random.rand(5) * 100,
            "high": np.random.rand(5) * 100,
            "low": np.random.rand(5) * 100,
            "close": np.random.rand(5) * 100,
            "volume": np.random.randint(1, 1000, size=5),
            "symbol": ["SYM"] * 5,
        }
    )

    monkeypatch.setattr(SignalEngine, "run", lambda self: df_in)
    se1 = SignalEngine()
    se2 = SignalEngine()

    df1 = se1.run()
    df2 = se2.run()

    # DataFrames should be identical
    pd.testing.assert_frame_equal(df1, df2)


# -----------------------------
# Integration / Pipeline Tests
# -----------------------------


def test_signal_engine_pipeline(monkeypatch):
    """
    Test SignalEngine output integrated in a downstream workflow:
    e.g., post-processing signals or feeding into a portfolio simulator.
    """
    df_in = pd.DataFrame(
        {
            "timestamp": pd.date_range("2025-01-01", periods=3),
            "open": [100, 101, 102],
            "high": [101, 102, 103],
            "low": [99, 100, 101],
            "close": [100, 101, 102],
            "volume": [1000, 1100, 1200],
            "symbol": ["SYM"] * 3,
        }
    ).astype({"open": "float", "high": "float", "low": "float", "close": "float"})

    monkeypatch.setattr(SignalEngine, "run", lambda self: df_in)

    # Simulate downstream workflow
    se = SignalEngine()
    df = se.run()

    # Example downstream step: simple signal generation
    df["signal"] = np.where(df["close"] > df["open"], "BUY", "SELL")

    # Validate pipeline behavior
    assert "signal" in df.columns
    assert all(s in ["BUY", "SELL"] for s in df["signal"])
    assert len(df) == 3


# -----------------------------
# Large Dataset Integration
# -----------------------------


@pytest.mark.parametrize("n_rows", [1000, 5000])
def test_signal_engine_large_pipeline(monkeypatch, n_rows):
    """
    Test SignalEngine with large datasets and simulate a downstream pipeline step.
    """
    df_in = pd.DataFrame(
        {
            "timestamp": pd.date_range("2025-01-01", periods=n_rows, freq="min"),
            "open": np.random.rand(n_rows) * 100,
            "high": np.random.rand(n_rows) * 100,
            "low": np.random.rand(n_rows) * 100,
            "close": np.random.rand(n_rows) * 100,
            "volume": np.random.randint(1, 1000, size=n_rows),
            "symbol": ["SYM"] * n_rows,
        }
    )

    monkeypatch.setattr(SignalEngine, "run", lambda self: df_in)
    se = SignalEngine()
    df = se.run()

    # Downstream example: moving average signal
    df["ma_signal"] = np.where(
        df["close"] > df["close"].rolling(3, min_periods=1).mean(), "UP", "DOWN"
    )

    # Validate results
    assert "ma_signal" in df.columns
    assert df["ma_signal"].isin(["UP", "DOWN"]).all()
    assert len(df) == n_rows
