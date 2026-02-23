import numpy as np
import pandas as pd

from qaai_system.screener.engine import ScreeningEngineSupercharged
from qaai_system.screener.feedback import ScreenerFeedback
from qaai_system.screener.explainability import ExplainabilityLogger


def make_sample_universe(n_symbols=10, n_days=30):
    syms = [f"S{idx}" for idx in range(n_symbols)]
    rows = []
    for s in syms:
        base = 100 + np.random.rand() * 20
        for i in range(n_days):
            price = base * (1 + 0.001 * i) + np.random.normal(0, 0.1)
            rows.append(
                {
                    "timestamp": pd.Timestamp("2025-01-01") + pd.Timedelta(days=i),
                    "open": price * (1 - 0.001),
                    "high": price * (1 + 0.002),
                    "low": price * (1 - 0.002),
                    "close": price,
                    "volume": int(1000 + 100 * np.random.rand()),
                    "symbol": s,
                }
            )
    return pd.DataFrame(rows)


def test_screen_filters_and_ranking(tmp_path):
    df = make_sample_universe(n_symbols=8, n_days=40)
    engine = ScreeningEngineSupercharged(
        w_rule=0.6,
        w_ml=0.4,
        feedback=ScreenerFeedback(alpha=0.1),
        explain_logger=ExplainabilityLogger(tmp_path / "scr.jsonl"),
    )
    results = engine.screen(df, top_k=5)
    assert isinstance(results, list)
    assert len(results) <= 5
    # ensure explain file created and contains one entry per symbol (latest run)
    lines = (tmp_path / "scr.jsonl").read_text().strip().splitlines()
    assert len(lines) == len(df["symbol"].unique())


def test_feedback_updates_reranks():
    df = make_sample_universe(n_symbols=6, n_days=30)
    fb = ScreenerFeedback(alpha=0.5)
    engine = ScreeningEngineSupercharged(
        w_rule=0.0, w_ml=1.0, feedback=fb
    )  # rely on ML/fb only
    # First run - neutral weights
    base = engine.screen(df, top_k=6)
    original_order = [s for s, _ in base]
    # Now simulate poor outcome for symbol original_order[0]
    sym_bad = original_order[0]
    fb.update(sym_bad, realized_pnl=-100.0, notional=1000.0)  # strong negative outcome
    new = engine.screen(df, top_k=6)
    new_order = [s for s, _ in new]
    assert sym_bad in original_order
    assert new_order.index(sym_bad) >= original_order.index(
        sym_bad
    )  # rank same or worse


def test_add_feedback_examples_and_online_fit():
    df = make_sample_universe(n_symbols=5, n_days=30)
    engine = ScreeningEngineSupercharged()
    # emulate multiple feedback examples
    for i in range(60):
        sym = f"S{i%5}"
        row = df[df["symbol"] == sym].iloc[-1]
        feats = [
            row["volume"],
            row["close"],
            row["close"] - row["low"],
            row["close"] - row["open"],
        ]
        label = 1 if i % 3 == 0 else 0
        engine.add_feedback_example(sym, feats, label)
    # After adding >=50 examples classifier should try to fit without exception
    # no exception implies pass
    assert True
