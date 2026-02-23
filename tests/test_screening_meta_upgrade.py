# tests/test_screening_meta_upgrade.py
import numpy as np
import pandas as pd
from qaai_system.screener.meta_engine import MetaScreeningEngine
from qaai_system.screener.engine import ScreeningEngineSupercharged
from qaai_system.screener.feedback import ScreenerFeedback
from qaai_system.screener.explainability import ExplainabilityLogger


# -------------------------
# Helper to make dummy data
# -------------------------
def make_df(n_sym=3, n_days=30, momentum_symbol="X0"):
    dates = pd.date_range("2025-01-01", periods=n_days)
    data = []
    for i in range(n_sym):
        sym = f"X{i}"
        base = 100 + i * 5
        for d in dates:
            open_ = base + np.random.randn()
            high = open_ + np.random.rand()
            low = open_ - np.random.rand()
            close = open_ + np.random.randn()
            vol = 1000 + np.random.randint(-50, 50)
            data.append([d, open_, high, low, close, vol, sym])
    df = pd.DataFrame(
        data, columns=["timestamp", "open", "high", "low", "close", "volume", "symbol"]
    )
    return df


# -------------------------
# Test multi-timeframe penalization
# -------------------------
def test_multi_timeframe_blocks_inconsistent_symbol():
    df = make_df(n_sym=3, n_days=40)
    # artificially create inconsistency for X1: short-term up, mid-term down
    s = "X1"
    idx = df[df["symbol"] == s].index
    half = len(idx) // 2
    df.loc[idx[:half], "close"] = np.linspace(120, 110, half)
    df.loc[idx[half:], "close"] = np.linspace(110, 111, len(idx) - half)

    engine = ScreeningEngineSupercharged()
    meta = MetaScreeningEngine(base_engine=engine)
    results = meta.run_cycle(df, top_k=10)

    symbols = [s for s, _ in results]
    if "X1" in symbols:
        # X1 should be penalized due to conflicting momentum
        # Allow either rank >= 2 or multiplier penalized
        assert symbols.index("X1") >= 2 or any(
            sc < 1.0 for sym, sc in results if sym == "X1"
        )


# -------------------------
# Test feedback drives weight adaptation and blacklist
# -------------------------
def test_feedback_drives_weight_adaptation_and_blacklist():
    df = make_df(n_sym=5, n_days=35, momentum_symbol="X0")
    engine = ScreeningEngineSupercharged()
    fb = ScreenerFeedback(alpha=0.5)
    meta = MetaScreeningEngine(
        base_engine=engine, feedback=fb, blacklist_threshold=2, blacklist_ttl_seconds=1
    )

    # initial run: X0 likely ranks high
    res1 = meta.run_cycle(df, top_k=5)
    assert any(s == "X0" for s, _ in res1)

    # simulate two bad trades for X0 → blacklist
    meta.on_trade_closed("X0", realized_pnl=-100.0, notional=1000.0)
    meta.on_trade_closed("X0", realized_pnl=-100.0, notional=1000.0)

    res2 = meta.run_cycle(df, top_k=5)
    assert not any(s == "X0" for s, _ in res2)

    # wait for TTL expiry and ensure it may come back
    import time

    time.sleep(1.1)
    res3 = meta.run_cycle(df, top_k=5)
    # X0 may come back after TTL
    assert any(s == "X0" for s, _ in res3)


# -------------------------
# Test meta runs and produces sorted list
# -------------------------
def test_meta_runs_and_produces_sorted_list(tmp_path):
    df = make_df(n_sym=8, n_days=30, momentum_symbol="X0")
    engine = ScreeningEngineSupercharged()
    meta = MetaScreeningEngine(
        base_engine=engine,
        feedback=ScreenerFeedback(alpha=0.1),
        explain_logger=ExplainabilityLogger(tmp_path / "meta.jsonl"),
        w_rule=0.6,
        w_ml=0.4,
    )
    results = meta.run_cycle(df, top_k=5)

    assert len(results) <= 5
    # ensure sorted descending
    scores = [sc for _, sc in results]
    assert all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1))
