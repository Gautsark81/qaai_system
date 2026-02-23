import pandas as pd
from modules.feature_engine.mutation_engine import MutationEngine


def test_pct_change_and_lag():
    df = pd.DataFrame({"close": [10, 20, 30, 40]})
    cfg = {"pct_change": ["close"], "lag": {"close": [1]}}

    m = MutationEngine(cfg)
    out = m.apply(df)

    assert "close_pct" in out.columns
    assert "close_lag1" in out.columns
    assert out.loc[1, "close_pct"] == 1.0
    assert out.loc[1, "close_lag1"] == 10


def test_rolling_mean_std():
    df = pd.DataFrame({"close": [1, 2, 3, 4, 5]})
    cfg = {"rolling": {"close": [{"window": 3, "op": "mean"}]}}

    out = MutationEngine(cfg).apply(df)

    assert "close_r3_mean" in out.columns
    assert abs(out.loc[2, "close_r3_mean"] - 2.0) < 1e-6


def test_clip_and_winsor():
    df = pd.DataFrame({"x": [-10, 0, 10]})
    cfg = {
        "clip": {"x": [-5, 5]},
        "winsor": {"x": [0.1, 0.9]},
    }

    out = MutationEngine(cfg).apply(df)

    assert out["x_clip"].max() == 5
    assert out["x_clip"].min() == -5
    assert "x_win" in out.columns
