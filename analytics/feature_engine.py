"""
Feature engine: robust, leakage-safe rolling features for meta-model training.

This file is a production-ready rewrite that preserves your original semantics
but is hardened for missing data, different date granularities and unit tests.

Primary functions:
- compute_rolling_features(trades, window_days=20) -> pd.DataFrame
- add_market_regime_features(df) -> pd.DataFrame
- compute_rolling_features_and_save(...)

This builds daily features keyed by (strategy_id, version, symbol, trade_date).
"""

from __future__ import annotations
from typing import Iterable, Optional, Union, Dict, Any
from pathlib import Path
import json
import math
import logging

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

TRADES_DIR = Path("data/trades")


def _load_trades_from_files(trades_dir: Path = TRADES_DIR) -> pd.DataFrame:
    rows = []
    if not trades_dir.exists():
        return pd.DataFrame(rows)
    for p in trades_dir.rglob("*.jsonl"):
        try:
            with p.open("r", encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if not ln:
                        continue
                    try:
                        rows.append(json.loads(ln))
                    except Exception:
                        continue
        except Exception:
            continue
    if not rows:
        return pd.DataFrame(rows)
    return pd.DataFrame(rows)


def _ensure_trade_columns(df: pd.DataFrame) -> pd.DataFrame:
    if "trade_date" not in df.columns:
        if "entry_ts" in df.columns:
            df["trade_date"] = pd.to_datetime(df["entry_ts"], errors="coerce").dt.strftime("%Y-%m-%d")
        else:
            df["trade_date"] = pd.NaT

    for col in ["pnl", "entry_price", "exit_price", "holding_period_minutes", "qty", "fees"]:
        if col not in df.columns:
            df[col] = 0.0 if col in {"pnl", "entry_price", "exit_price", "fees"} else 0
    df["pnl"] = pd.to_numeric(df["pnl"], errors="coerce").fillna(0.0)
    df["entry_price"] = pd.to_numeric(df["entry_price"], errors="coerce").fillna(0.0)
    df["exit_price"] = pd.to_numeric(df["exit_price"], errors="coerce").fillna(df["entry_price"])
    df["holding_period_minutes"] = pd.to_numeric(df["holding_period_minutes"], errors="coerce").fillna(0).astype(int)
    df["qty"] = pd.to_numeric(df["qty"], errors="coerce").fillna(1).astype(int)

    for col in ("strategy_id", "version", "symbol"):
        if col not in df.columns:
            df[col] = None
    df["strategy_id"] = df["strategy_id"].fillna("fallback").astype(str)
    df["version"] = df["version"].fillna("v0").astype(str)
    df["symbol"] = df["symbol"].astype(str)

    if "entry_ts" in df.columns:
        df["entry_dt"] = pd.to_datetime(df["entry_ts"], errors="coerce")
    else:
        df["entry_dt"] = pd.NaT

    if "exit_ts" in df.columns:
        df["exit_dt"] = pd.to_datetime(df["exit_ts"], errors="coerce")
    else:
        df["exit_dt"] = df["entry_dt"]

    df["trade_date"] = df["trade_date"].astype(str)
    return df


def add_market_regime_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add volatility regime flags based on atr_ratio quantiles per-symbol.
    """
    if df.empty:
        return df

    df = df.copy()
    df["atr_ratio"] = pd.to_numeric(df.get("atr_ratio", 0.0), errors="coerce").fillna(0.0)

    def regime_for_group(g):
        if g["atr_ratio"].nunique() <= 1:
            g["volatility_regime_high"] = 0
            g["volatility_regime_low"] = 0
            return g
        hi = g["atr_ratio"].quantile(0.75)
        lo = g["atr_ratio"].quantile(0.25)
        g["volatility_regime_high"] = (g["atr_ratio"] >= hi).astype(int)
        g["volatility_regime_low"] = (g["atr_ratio"] <= lo).astype(int)
        return g

    try:
        df = df.groupby("symbol", group_keys=False).apply(regime_for_group)
    except Exception:
        hi = df["atr_ratio"].quantile(0.75)
        lo = df["atr_ratio"].quantile(0.25)
        df["volatility_regime_high"] = (df["atr_ratio"] >= hi).astype(int)
        df["volatility_regime_low"] = (df["atr_ratio"] <= lo).astype(int)

    df["volatility_regime_high"] = df["volatility_regime_high"].astype(int)
    df["volatility_regime_low"] = df["volatility_regime_low"].astype(int)
    return df.reset_index(drop=True)


def compute_rolling_features(trades: Optional[Union[pd.DataFrame, Iterable[Dict[str, Any]]]] = None, window_days: int = 20) -> pd.DataFrame:
    """
    Compute rolling features keyed by (strategy_id,version,symbol,trade_date).

    Returns DataFrame with columns:
      strategy_id, version, symbol, trade_date,
      rolling_trades_{window_days}, rolling_win_rate_{window_days},
      rolling_profit_factor_50, rolling_net_pnl_{window_days},
      avg_holding_min_{window_days}, sl_hit_rate_{window_days}, tp_hit_rate_{window_days},
      atr_ratio, volatility_regime_high, volatility_regime_low
    """
    if trades is None:
        trades_df = _load_trades_from_files()
    elif isinstance(trades, pd.DataFrame):
        trades_df = trades.copy()
    else:
        trades_df = pd.DataFrame(list(trades))

    if trades_df.empty:
        raise ValueError("No trades available to compute features")

    trades_df = _ensure_trade_columns(trades_df)

    agg = trades_df.groupby(["strategy_id", "version", "symbol", "trade_date"], sort=False).agg(
        trades_count=("order_id", "count"),
        wins=("pnl", lambda s: (s > 0).sum()),
        losses=("pnl", lambda s: (s <= 0).sum()),
        net_pnl=("pnl", "sum"),
        avg_holding_min=("holding_period_minutes", "mean"),
        sl_hit=("sl_hit", "sum"),
        tp_hit=("tp_hit", "sum"),
        avg_entry_price=("entry_price", "mean"),
        avg_exit_price=("exit_price", "mean"),
        fees=("fees", "sum"),
    ).reset_index()

    agg["trades_count"] = agg["trades_count"].astype(int)
    agg["wins"] = agg["wins"].astype(int)
    agg["losses"] = agg["losses"].astype(int)
    agg["net_pnl"] = pd.to_numeric(agg["net_pnl"], errors="coerce").fillna(0.0)
    agg["avg_holding_min"] = pd.to_numeric(agg["avg_holding_min"], errors="coerce").fillna(0.0)
    agg["sl_hit"] = pd.to_numeric(agg["sl_hit"], errors="coerce").fillna(0).astype(int)
    agg["tp_hit"] = pd.to_numeric(agg["tp_hit"], errors="coerce").fillna(0).astype(int)

    agg["trade_date_dt"] = pd.to_datetime(agg["trade_date"], format="%Y-%m-%d", errors="coerce")
    agg = agg.sort_values(["strategy_id", "version", "symbol", "trade_date_dt"]).reset_index(drop=True)

    out = []
    grouped = agg.groupby(["strategy_id", "version", "symbol"], sort=False)
    for (sid, ver, sym), g in grouped:
        g = g.sort_values("trade_date_dt").reset_index(drop=True)
        if g.empty:
            continue
        for i, row in g.iterrows():
            cur_date = row["trade_date_dt"]
            window_start = cur_date - pd.Timedelta(days=window_days)
            window_slice = g[(g["trade_date_dt"] > window_start) & (g["trade_date_dt"] <= cur_date)]

            trades_count = int(window_slice["trades_count"].sum())
            wins = int(window_slice["wins"].sum())
            losses = int(window_slice["losses"].sum())
            net_pnl = float(window_slice["net_pnl"].sum())
            avg_holding = float(window_slice["avg_holding_min"].mean()) if not window_slice.empty else 0.0
            sl_rate = float(window_slice["sl_hit"].sum()) / trades_count if trades_count > 0 else 0.0
            tp_rate = float(window_slice["tp_hit"].sum()) / trades_count if trades_count > 0 else 0.0

            # profit factor over 50-day window
            pf_window_start = cur_date - pd.Timedelta(days=50)
            pf_slice = g[(g["trade_date_dt"] > pf_window_start) & (g["trade_date_dt"] <= cur_date)]
            gross_win = float(pf_slice[pf_slice["net_pnl"] > 0]["net_pnl"].sum())
            gross_loss = -float(pf_slice[pf_slice["net_pnl"] < 0]["net_pnl"].sum()) if not pf_slice[pf_slice["net_pnl"] < 0].empty else 0.0
            if gross_loss == 0.0:
                profit_factor = float("inf") if gross_win > 0 else 1.0
            else:
                profit_factor = gross_win / gross_loss if gross_loss > 0 else 1.0

            # atr_ratio approximation
            slice_prices = window_slice[["avg_entry_price", "avg_exit_price"]].dropna()
            if not slice_prices.empty:
                ranges = (slice_prices["avg_exit_price"] - slice_prices["avg_entry_price"]).abs()
                avg_range = float(ranges.mean())
                base_price = float(slice_prices["avg_entry_price"].replace(0, np.nan).dropna().mean() or np.nan)
                atr_ratio = (avg_range / base_price) if (not np.isnan(base_price) and base_price > 0) else 0.0
            else:
                atr_ratio = 0.0

            out.append({
                "strategy_id": sid,
                "version": ver,
                "symbol": sym,
                "trade_date": row["trade_date"],
                f"rolling_trades_{window_days}": trades_count,
                f"rolling_win_rate_{window_days}": (wins / trades_count) if trades_count > 0 else 0.0,
                "rolling_profit_factor_50": profit_factor,
                f"rolling_net_pnl_{window_days}": net_pnl,
                f"avg_holding_min_{window_days}": avg_holding,
                f"sl_hit_rate_{window_days}": sl_rate,
                f"tp_hit_rate_{window_days}": tp_rate,
                "atr_ratio": atr_ratio,
            })

    features = pd.DataFrame(out)
    if features.empty:
        raise ValueError("No features produced from trades")

    # regime indicators
    features = add_market_regime_features(features)

    # ensure columns exist
    expected = [
        f"rolling_trades_{window_days}",
        f"rolling_win_rate_{window_days}",
        "rolling_profit_factor_50",
        f"rolling_net_pnl_{window_days}",
        f"avg_holding_min_{window_days}",
        f"sl_hit_rate_{window_days}",
        f"tp_hit_rate_{window_days}",
        "atr_ratio",
        "volatility_regime_high",
        "volatility_regime_low",
    ]
    for c in expected:
        if c not in features.columns:
            features[c] = 0.0

    features = features.sort_values(["strategy_id", "version", "symbol", "trade_date"]).reset_index(drop=True)
    return features


def compute_rolling_features_and_save(trades: Optional[Union[pd.DataFrame, Iterable[Dict[str, Any]]]] = None, window_days: int = 20, out_path: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    df = compute_rolling_features(trades, window_days=window_days)
    if out_path:
        outp = Path(out_path)
        outp.parent.mkdir(parents=True, exist_ok=True)
        if outp.suffix == ".csv":
            df.to_csv(outp, index=False)
        else:
            df.to_parquet(outp, index=False)
    return df
