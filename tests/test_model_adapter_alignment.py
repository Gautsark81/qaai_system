# tests/test_model_adapter_alignment.py
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

from strategies.strategy_engine import ModelAdapter

def make_dummy_model(feature_cols):
    X = pd.DataFrame(np.random.randn(100, len(feature_cols)), columns=feature_cols)
    y = (X[feature_cols[0]] > 0).astype(int)
    pipe = Pipeline([("scaler", StandardScaler()), ("rf", RandomForestClassifier(n_estimators=5, random_state=1))])
    pipe.fit(X, y)
    return pipe

def test_model_adapter_alignment(tmp_path):
    feature_cols = ["a", "b", "c"]
    model = make_dummy_model(feature_cols)
    art = {"model": model, "feature_columns": feature_cols}
    p = tmp_path / "m.pkl"
    with p.open("wb") as fh:
        pickle.dump(art, fh)

    adapter = ModelAdapter.load(str(p))

    # Provide a runtime DF missing 'a' and with an extra 'symbol' column
    df_runtime = pd.DataFrame({"b": [0.1], "c": [0.2], "symbol": ["FOO"]})
    proba = adapter.predict_proba(df_runtime)
    assert proba.shape[0] == 1
    assert proba.shape[1] >= 2
