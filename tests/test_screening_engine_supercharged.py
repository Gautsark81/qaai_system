# tests/test_screening_engine_supercharged.py

import pandas as pd
import numpy as np
from qaai_system.screener.supercharged_engine import ScreeningEngineSupercharged
from qaai_system.utils.explainability import ExplainabilityLogger


def make_df(n_sym=5, n_days=30, seed=42):
    """Helper: generate synthetic OHLCV data"""
    np.random.seed(seed)
    rows = []
    for s in range(n_sym):
        symbol = f"S{s}"
        price = 100.0
        for d in range(n_days):
            ret = np.random.normal(0, 0.01)
            price *= 1 + ret
            rows.append(
                {
                    "timestamp": pd.Timestamp("2025-01-01") + pd.Timedelta(days=d),
                    "open": price * (1 - 0.005),
                    "high": price * (1 + 0.01),
                    "low": price * (1 - 0.01),
                    "close": price,
                    "volume": np.random.randint(1000, 2000),
                    "symbol": symbol,
                }
            )
    return pd.DataFrame(rows)


def test_engine_runs_and_returns_sorted_list(tmp_path):
    df = make_df(n_sym=5, n_days=40)
    logger = ExplainabilityLogger(tmp_path / "exp.jsonl")
    engine = ScreeningEngineSupercharged(w_rule=0.6, w_ml=0.4, explain_logger=logger)

    results = engine.screen(df, top_k=3)

    assert isinstance(results, list)
    assert len(results) == 3
    assert all(isinstance(s, tuple) and len(s) == 2 for s in results)
    assert results == sorted(results, key=lambda x: x[1], reverse=True)

    # Check explainability log file exists and has entries
    logs = list(logger.read())
    assert len(logs) >= 3
    assert "rule_score" in logs[0]
    assert "ml_score" in logs[0]
    assert "final_score" in logs[0]


def test_rule_and_ml_scores_reasonable():
    df = make_df(n_sym=1, n_days=20)
    engine = ScreeningEngineSupercharged()

    features = engine._compute_features(df)
    row = features.iloc[-1]

    rule = engine._rule_score(row)
    ml = engine._ml_score(row)

    assert 0.0 <= rule <= 1.0
    assert 0.0 <= ml <= 1.0


def test_weights_affect_final_score():
    df = make_df(n_sym=1, n_days=25)
    engine1 = ScreeningEngineSupercharged(w_rule=1.0, w_ml=0.0)
    engine2 = ScreeningEngineSupercharged(w_rule=0.0, w_ml=1.0)

    results1 = engine1.screen(df, top_k=1)
    results2 = engine2.screen(df, top_k=1)

    # With extreme weights, scores should differ
    assert results1[0][1] != results2[0][1]


def test_topk_limits_results():
    df = make_df(n_sym=8, n_days=30)
    engine = ScreeningEngineSupercharged()
    results = engine.screen(df, top_k=5)

    assert len(results) == 5
    symbols = [s for s, _ in results]
    assert len(set(symbols)) == 5  # no duplicates
