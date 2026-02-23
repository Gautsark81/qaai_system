### 📁 FILE: tests/test_watchlist_manager.py

import pandas as pd
import numpy as np
from watchlist.watchlist_manager import build_watchlist, filter_for_signal_generation


def mock_stock_data(n=200):
    np.random.seed(42)
    df = pd.DataFrame(
        {
            "symbol": [f"STOCK{i}" for i in range(n)],
            "signal_strength": np.random.rand(n),
            "rsi": np.random.rand(n) * 100,
            "ma_ratio": np.random.rand(n) * 2,
            "atr": np.random.rand(n) * 5,
            "bbw": np.random.rand(n) * 0.1,
            "eps": np.random.rand(n) * 50,
            "pe_ratio": np.random.rand(n) * 30,
            "roe": np.random.rand(n) * 20,
        }
    )
    return df


def mock_signal_data():
    return pd.DataFrame(
        {
            "symbol": ["STOCK1", "STOCK2", "STOCK101", "STOCK150"],
            "signal_strength": [0.7, 0.8, 0.6, 0.9],
        }
    )


def test_watchlist_top_k():
    df = mock_stock_data()
    watchlist = build_watchlist(df, top_k=100)
    assert len(watchlist) == 100
    assert "final_score" in watchlist.columns


def test_watchlist_ranking_order():
    df = mock_stock_data()
    watchlist = build_watchlist(df, top_k=10)
    assert watchlist.iloc[0]["final_score"] >= watchlist.iloc[-1]["final_score"]


def test_filter_for_signal_generation():
    stock_df = mock_stock_data()
    watchlist = build_watchlist(stock_df, top_k=50)
    signal_df = mock_signal_data()
    filtered = filter_for_signal_generation(signal_df, watchlist)
    assert all(filtered["symbol"].isin(watchlist["symbol"]))
