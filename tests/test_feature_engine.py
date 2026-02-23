import pandas as pd
import numpy as np
from analytics.feature_engine import compute_rolling_features, add_market_regime_features, compute_rolling_features_and_save

def make_sample_trades():
    # produce trades across multiple days for a single strategy/symbol
    rows = []
    base_date = pd.to_datetime("2021-01-01")
    for i in range(8):
        d = (base_date + pd.Timedelta(days=i)).strftime("%Y-%m-%d")
        # create 1..3 trades per day
        for j in range(1 + (i % 3)):
            rows.append({
                "strategy_id": "s1",
                "version": "v1",
                "symbol": "SYM",
                "order_id": f"o_{i}_{j}",
                "entry_ts": (base_date + pd.Timedelta(days=i) + pd.Timedelta(minutes=j)).isoformat(),
                "exit_ts": (base_date + pd.Timedelta(days=i) + pd.Timedelta(minutes=j+5)).isoformat(),
                "entry_price": 100.0 + i * 0.5 + j * 0.1,
                "exit_price": 100.5 + i * 0.5 + j * 0.1,
                "qty": 1,
                "pnl": 0.5 if (i % 2 == 0) else -0.25,
                "holding_period_minutes": 5,
                "sl_hit": False,
                "tp_hit": True,
                "fees": 0.0,
                "trade_date": d,
            })
    return rows


def test_compute_rolling_features_minimal():
    trades = make_sample_trades()
    feats = compute_rolling_features(trades, window_days=3)
    # ensure features DataFrame contains expected columns
    expected_cols = [
        "strategy_id",
        "version",
        "symbol",
        "trade_date",
        "rolling_trades_3",
        "rolling_win_rate_3",
        "rolling_profit_factor_50",
        "rolling_net_pnl_3",
        "avg_holding_min_3",
        "sl_hit_rate_3",
        "tp_hit_rate_3",
        "atr_ratio",
        "volatility_regime_high",
        "volatility_regime_low",
    ]
    for c in expected_cols:
        assert c in feats.columns

    # per-day grouping: there should be at least as many feature rows as unique trade_date values
    unique_dates = len(set([r["trade_date"] for r in trades]))
    assert feats.shape[0] >= unique_dates

    # verify numeric ranges
    assert (feats["rolling_trades_3"] >= 0).all()
    assert (feats["rolling_win_rate_3"] >= 0).all()
    assert (feats["rolling_win_rate_3"] <= 1).all()


def test_add_market_regime_features_edgecase():
    # empty DataFrame handled gracefully
    empty = pd.DataFrame()
    out = add_market_regime_features(empty)
    # empty should return empty
    assert out.empty or ("volatility_regime_high" in out.columns and "volatility_regime_low" in out.columns)

def test_compute_rolling_features_and_save(tmp_path):
    trades = make_sample_trades()
    out_file = tmp_path / "features.parquet"
    df = compute_rolling_features_and_save(trades, window_days=3, out_path=str(out_file))
    assert out_file.exists()
    loaded = pd.read_parquet(out_file)
    assert loaded.shape[0] == df.shape[0]
