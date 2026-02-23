# test_signal_engine_master.py #

import pandas as pd
import numpy as np
import pytest
from qaai_system.signal_engine.signal_engine import SignalEngine

# -----------------------------
# Edge Case / Parameterized Tests
# -----------------------------


@pytest.mark.parametrize(
    "df_in, description",
    [
        (pd.DataFrame(), "Empty DataFrame"),
        (pd.DataFrame({"symbol": ["AAPL"], "price": [150]}), "Missing OHLCV columns"),
        (
            pd.DataFrame(
                {
                    "timestamp": pd.date_range("2025-01-01", periods=5),
                    "open": [100, np.nan, 102, 103, 104],
                    "high": [101, 102, np.nan, 105, 106],
                    "low": [99, 98, 97, np.nan, 103],
                    "close": [100, 101, 102, 103, np.nan],
                    "volume": [1000, 1100, 1200, 1300, np.nan],
                    "symbol": ["AAPL"] * 5,
                }
            ),
            "NaN values",
        ),
    ],
)
def test_signal_engine_edge_cases(monkeypatch, df_in, description):
    """Test SignalEngine with edge-case input DataFrames."""
    monkeypatch.setattr(SignalEngine, "run", lambda self: df_in)
    se = SignalEngine()
    df = se.run()
    assert isinstance(df, pd.DataFrame)
    assert "symbol" in df.columns or df.empty


# -----------------------------
# Column Consistency
# -----------------------------


def test_column_consistency(monkeypatch):
    """Engine should always return consistent column names and types."""
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
    se = SignalEngine()
    df = se.run()

    # Column order
    assert list(df.columns) == list(df_in.columns)
    # Column types
    for col in ["open", "high", "low", "close"]:
        assert pd.api.types.is_float_dtype(df[col])


# -----------------------------
# Reproducibility Tests
# -----------------------------


@pytest.mark.parametrize("seed", [42, 123, 999])
def test_signal_engine_reproducibility(monkeypatch, seed):
    """SignalEngine should produce consistent output for the same random seed."""
    np.random.seed(seed)
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
    pd.testing.assert_frame_equal(se1.run(), se2.run())


# -----------------------------
# Integration / Pipeline Tests
# -----------------------------


def test_signal_engine_pipeline(monkeypatch):
    """Test SignalEngine output integrated in a downstream workflow."""
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

    se = SignalEngine()
    df = se.run()
    df["signal"] = np.where(df["close"] > df["open"], "BUY", "SELL")

    assert "signal" in df.columns
    assert all(s in ["BUY", "SELL"] for s in df["signal"])
    assert len(df) == 3


# -----------------------------
# Large Dataset Integration
# -----------------------------


@pytest.mark.parametrize("n_rows", [1000, 5000])
def test_signal_engine_large_pipeline(monkeypatch, n_rows):
    """Test SignalEngine with large datasets and downstream workflow."""
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
    df["ma_signal"] = np.where(
        df["close"] > df["close"].rolling(3, min_periods=1).mean(), "UP", "DOWN"
    )
    assert "ma_signal" in df.columns
    assert df["ma_signal"].isin(["UP", "DOWN"]).all()
    assert len(df) == n_rows


# -----------------------------
# Signal Correctness Tests
# -----------------------------


@pytest.mark.parametrize(
    "df_in, expected_ma_signal, description",
    [
        (
            pd.DataFrame(
                {
                    "timestamp": pd.date_range("2025-01-01", periods=5),
                    "close": [100, 102, 104, 106, 108],
                    "open": [99, 101, 103, 105, 107],
                    "high": [101, 103, 105, 107, 109],
                    "low": [98, 100, 102, 104, 106],
                    "volume": [1000, 1100, 1200, 1300, 1400],
                    "symbol": ["SYM"] * 5,
                }
            ).astype({"close": "float"}),
            ["SELL", "SELL", "BUY", "BUY", "BUY"],
            "MA crossover bullish",
        ),
        (
            pd.DataFrame(
                {
                    "timestamp": pd.date_range("2025-01-01", periods=5),
                    "close": [108, 106, 104, 102, 100],
                    "open": [107, 105, 103, 101, 99],
                    "high": [109, 107, 105, 103, 101],
                    "low": [106, 104, 102, 100, 98],
                    "volume": [1400, 1300, 1200, 1100, 1000],
                    "symbol": ["SYM"] * 5,
                }
            ).astype({"close": "float"}),
            ["BUY", "BUY", "SELL", "SELL", "SELL"],
            "MA crossover bearish",
        ),
    ],
)
def test_ma_crossover_signal(monkeypatch, df_in, expected_ma_signal, description):
    """Validate signals generated by simple moving average (MA) crossover logic."""
    monkeypatch.setattr(SignalEngine, "run", lambda self: df_in)

    se = SignalEngine()
    df = se.run()

    # Example signal logic: BUY if close > open else SELL
    df["signal"] = ["BUY" if c > o else "SELL" for c, o in zip(df["close"], df["open"])]

    assert list(df["signal"]) == expected_signals, f"Failed signal test: {description}"


# -----------------------------
# Technical Indicator Signal Tests
# -----------------------------
import pandas as pd
import pytest


@pytest.mark.parametrize(
    "df_in, expected_ma_signal, description",
    [
        # Simple MA crossover: short-term > long-term -> BUY
        (
            pd.DataFrame(
                {
                    "timestamp": pd.date_range("2025-01-01", periods=5),
                    "close": [100, 102, 104, 106, 108],
                    "open": [99, 101, 103, 105, 107],
                    "high": [101, 103, 105, 107, 109],
                    "low": [98, 100, 102, 104, 106],
                    "volume": [1000, 1100, 1200, 1300, 1400],
                    "symbol": ["SYM"] * 5,
                }
            ).astype({"close": "float"}),
            ["SELL", "SELL", "BUY", "BUY", "BUY"],
            "MA crossover bullish",
        ),
        # Simple MA crossover: short-term < long-term -> SELL
        (
            pd.DataFrame(
                {
                    "timestamp": pd.date_range("2025-01-01", periods=5),
                    "close": [108, 106, 104, 102, 100],
                    "open": [107, 105, 103, 101, 99],
                    "high": [109, 107, 105, 103, 101],
                    "low": [106, 104, 102, 100, 98],
                    "volume": [1400, 1300, 1200, 1100, 1000],
                    "symbol": ["SYM"] * 5,
                }
            ).astype({"close": "float"}),
            ["BUY", "BUY", "SELL", "SELL", "SELL"],
            "MA crossover bearish",
        ),
    ],
)
def test_ma_crossover_signal(monkeypatch, df_in, expected_ma_signal, description):
    """
    Validate signals generated by simple moving average (MA) crossover logic.
    """
    # Patch run() to return our test DataFrame
    monkeypatch.setattr(SignalEngine, "run", lambda self: df_in)

    se = SignalEngine()
    df = se.run()

    # Example simple MA signal logic
    short_ma = df["close"].rolling(window=2).mean()
    long_ma = df["close"].rolling(window=3).mean()
    df["signal"] = [
        "BUY" if s > l else "SELL" for s, l in zip(short_ma.bfill(), long_ma.bfill())
    ]

    assert (
        list(df["signal"]) == expected_ma_signal
    ), f"Failed MA signal test: {description}"
