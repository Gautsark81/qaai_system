import pandas as pd
import numpy as np
import pytest
from qaai_system.signal_engine.signal_engine import SignalEngine

# -----------------------------
# Parameterized Edge Tests
# -----------------------------


@pytest.mark.parametrize(
    "df_input, expected_empty",
    [
        (pd.DataFrame(), True),  # empty DataFrame
        (pd.DataFrame({"symbol": ["AAPL"], "price": [150]}), False),  # missing OHLCV
        (
            pd.DataFrame(
                {
                    "timestamp": pd.date_range("2025-01-01", periods=3),
                    "open": [100, np.nan, 102],
                    "high": [101, 102, np.nan],
                    "low": [99, 98, 97],
                    "close": [100, 101, 102],
                    "volume": [1000, 1100, np.nan],
                    "symbol": ["SYM"] * 3,
                }
            ).astype(
                {"open": "float", "high": "float", "low": "float", "close": "float"}
            ),
            False,
        ),
    ],
)
def test_signal_engine_various_inputs(monkeypatch, df_input, expected_empty):
    """Test SignalEngine with different edge DataFrames."""
    monkeypatch.setattr(SignalEngine, "run", lambda self: df_input)
    se = SignalEngine()
    df = se.run()
    assert isinstance(df, pd.DataFrame)
    assert df.empty == expected_empty


@pytest.mark.parametrize("n_rows", [10, 100, 1000])  # small to medium datasets
def test_signal_engine_dataset_scaling(monkeypatch, n_rows):
    """Test scaling to different dataset sizes."""
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
    assert len(df) == n_rows
    assert "symbol" in df.columns


@pytest.mark.parametrize(
    "col_dtypes",
    [
        {
            "open": "float",
            "high": "float",
            "low": "float",
            "close": "float",
        },  # correct types
        {"open": "int", "high": "int", "low": "int", "close": "int"},  # integer inputs
    ],
)
def test_signal_engine_column_types(monkeypatch, col_dtypes):
    """Ensure columns are consistently typed as expected."""
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
    ).astype(col_dtypes)
    monkeypatch.setattr(SignalEngine, "run", lambda self: df_in)
    se = SignalEngine()
    df = se.run()
    for col, dtype in col_dtypes.items():
        if dtype == "float":
            assert pd.api.types.is_float_dtype(df[col])
        elif dtype == "int":
            assert pd.api.types.is_integer_dtype(df[col])
