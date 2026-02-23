# tests/test_watchlist_advanced.py
import numpy as np
import pandas as pd
from qaai_system.watchlist_advanced import AdvancedWatchlist


def _make_df(n_sym=6, n_days=40, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    start = pd.Timestamp("2025-01-01")
    for i in range(n_sym):
        sym = f"S{i}"
        price = 100 + rng.uniform(-2, 2)
        for d in range(n_days):
            ts = start + pd.Timedelta(days=d)
            # controlled drift + noise
            price *= 1.0 + 0.001 * (i + 1) + rng.normal(0, 0.005)
            high = price * (1 + rng.uniform(0.0, 0.01))
            low = price * (1 - rng.uniform(0.0, 0.01))
            open_ = price * (1 + rng.normal(0, 0.002))
            close = price
            vol = int(900 + 50 * i + rng.integers(0, 100))
            rows.append((ts, open_, high, low, close, vol, sym))
    return pd.DataFrame(
        rows, columns=["timestamp", "open", "high", "low", "close", "volume", "symbol"]
    )


def test_risk_weights_sum_and_caps():
    df = _make_df(n_sym=5, n_days=60, seed=42)
    aw = AdvancedWatchlist()
    items = aw.build_watchlist(df, top_k=5, risk_budget=1.0, per_symbol_cap=0.35)
    assert 1 <= len(items) <= 5
    total_w = sum(i.weight for i in items)
    # Allow small numerical tolerance
    assert 0.95 <= total_w <= 1.05
    # Ensure no one exceeds cap
    assert max(i.weight for i in items) <= 0.35 + 1e-9


def test_reasons_have_expected_keys():
    df = _make_df(n_sym=4, n_days=50, seed=7)
    aw = AdvancedWatchlist()
    items = aw.build_watchlist(df, top_k=4, risk_budget=0.8, per_symbol_cap=0.5)
    assert len(items) > 0
    keys = {"momentum", "volume_pressure", "volatility"}
    for it in items:
        assert keys.issubset(set(it.reasons.keys()))


def test_adaptive_refresh_reacts_to_vol_and_churn():
    df = _make_df(n_sym=6, n_days=50, seed=11)
    aw = AdvancedWatchlist(base_refresh_s=20, min_refresh_s=5, max_refresh_s=60)
    # First build
    items1 = aw.build_watchlist(df, top_k=5, risk_budget=1.0, per_symbol_cap=0.4)
    t1 = aw.next_refresh_seconds(df, items1)
    # Simulate churn by replacing items with different symbols, and higher vol
    # increase vol by multiplying recent returns
    df2 = df.copy()
    mask = df2["timestamp"] > df2["timestamp"].max() - pd.Timedelta(days=15)
    df2.loc[mask, "close"] *= 1.0 + 0.03  # boost recent volatility
    items2 = aw.build_watchlist(df2, top_k=5, risk_budget=1.0, per_symbol_cap=0.4)
    t2 = aw.next_refresh_seconds(df2, items2)
    # Expect faster refresh when vol/churn rises
    assert aw.min_refresh_s <= t2 <= aw.max_refresh_s
    assert t2 <= t1
