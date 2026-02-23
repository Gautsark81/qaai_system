# tests/test_screener_to_watchlist.py
import pandas as pd
import numpy as np
from qaai_system.screener.engine import ScreeningEngineSupercharged
from qaai_system.screener.feedback import ScreenerFeedback
from qaai_system.screener.explainability import ExplainabilityLogger
from qaai_system.integrations.screener_watchlist import sync_screen_to_watchlist


def make_sample_universe(n_symbols=6, n_days=20):
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


class MockWatchlistManagerA:
    """Preferred API: update_watchlist(list_of_tuples)"""

    def __init__(self):
        self.items = []

    def update_watchlist(self, items):
        # items: list of (symbol, score)
        self.items = list(items)


class MockWatchlistManagerB:
    """Fallback API: clear() and add(symbol, score)"""

    def __init__(self):
        self.items = []

    def clear(self):
        self.items = []

    def add(self, symbol, score):
        self.items.append((symbol, score))


def test_sync_updates_preferred_api(tmp_path):
    df = make_sample_universe()
    engine = ScreeningEngineSupercharged(
        feedback=ScreenerFeedback(alpha=0.1),
        explain_logger=ExplainabilityLogger(tmp_path / "scr.jsonl"),
    )
    wm = MockWatchlistManagerA()
    pushed = sync_screen_to_watchlist(
        engine, wm, df, top_k=3, score_threshold=0.0, explain=True
    )
    # watchlist manager items should match pushed list
    assert wm.items == pushed
    assert len(wm.items) <= 3
    # ensure symbols exist and are unique
    syms = [s for s, _ in wm.items]
    assert len(syms) == len(set(syms))


def test_sync_updates_fallback_api():
    df = make_sample_universe()
    engine = ScreeningEngineSupercharged()
    wm = MockWatchlistManagerB()
    pushed = sync_screen_to_watchlist(engine, wm, df, top_k=4, score_threshold=0.0)
    assert len(wm.items) == len(pushed)
    assert all(isinstance(x[0], str) and isinstance(x[1], float) for x in pushed)
