# 📁 tests/test_selector_utils.py

import pandas as pd
import numpy as np

from qaai_system.signal_engine.selector_utils import generate_features


def mock_price_data(n: int = 50):
    """Create random OHLCV data for testing."""
    np.random.seed(42)
    return pd.DataFrame(
        {
            "open": np.random.uniform(100, 200, n),
            "high": np.random.uniform(100, 205, n),
            "low": np.random.uniform(95, 200, n),
            "close": np.random.uniform(100, 210, n),
            "volume": np.random.randint(10000, 50000, n),
        }
    )


def test_generate_features_shape():
    df = mock_price_data()
    features = generate_features(df)
    assert isinstance(features, pd.DataFrame)
    # Should have same number of rows
    assert features.shape[0] == df.shape[0]


def test_generate_features_expected_columns():
    df = mock_price_data()
    features = generate_features(df)
    expected_cols = ["returns", "ma_ratio", "rsi", "atr", "bbw"]
    for col in expected_cols:
        assert col in features.columns, f"Missing column {col}"


def test_generate_features_nan_safe():
    df = mock_price_data()
    features = generate_features(df)
    # Should not produce NaN
    assert not features.isnull().any().any()


def test_generate_features_return_types():
    df = mock_price_data()
    features = generate_features(df)
    # All outputs numeric
    assert features.dtypes.apply(lambda x: np.issubdtype(x, np.number)).all()


def test_generate_features_empty_input():
    df = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    features = generate_features(df)
    # Should return empty DataFrame with correct columns
    assert list(features.columns) == ["returns", "ma_ratio", "rsi", "atr", "bbw"]
    assert features.empty
