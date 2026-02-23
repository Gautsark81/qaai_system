### 📁 FILE: tests/test_watchlist_ml.py

import pandas as pd
import numpy as np
from screening.watchlist_ml import train_model, score_candidates
from sklearn.linear_model import LogisticRegression


def mock_data():
    np.random.seed(42)
    return pd.DataFrame(
        {
            "open": np.random.uniform(100, 200, 100),
            "high": np.random.uniform(100, 200, 100),
            "low": np.random.uniform(90, 195, 100),
            "close": np.random.uniform(95, 205, 100),
            "volume": np.random.randint(10000, 50000, 100),
            "atr": np.random.uniform(2, 10, 100),
            "label": np.random.randint(0, 2, 100),
        }
    )


def test_train_model_logistic():
    df = mock_data()
    model = train_model(df, label_col="label", model_type="logistic")
    assert isinstance(model, LogisticRegression)


def test_score_candidates_output():
    df = mock_data()
    model = train_model(df, label_col="label")
    ranked = score_candidates(df.drop(columns=["label"]), model)
    assert not ranked.empty
    assert "signal_strength" in ranked.columns
    assert "adaptive_sl" in ranked.columns
    assert "adaptive_tp" in ranked.columns


def test_score_candidates_conf_threshold():
    df = mock_data()
    model = train_model(df, label_col="label")
    result = score_candidates(
        df.drop(columns=["label"]), model, confidence_threshold=0.9
    )
    assert all(result["signal_strength"] >= 0.9)


def test_score_candidates_top_k():
    df = mock_data()
    model = train_model(df, label_col="label")
    result = score_candidates(df.drop(columns=["label"]), model, top_k=5)
    assert len(result) <= 5
