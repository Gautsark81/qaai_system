# qaai_system/analytics/target_builder.py
from __future__ import annotations
import logging
from pathlib import Path
from typing import Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

def build_forward_targets(trades_df: pd.DataFrame, window_days: int = 5) -> pd.DataFrame:
    """
    Construct forward-window targets at (strategy, version, symbol, date) level:
    For each trade_date, compute whether the cumulative net_pnl over next `window_days`
    is positive. Return DataFrame with column 'target_next_{window}_days' (0/1).
    """
    df = trades_df.copy()
    # ensure trade_date is normalized date
    if "exit_ts" in df.columns:
        df["trade_date"] = pd.to_datetime(df["exit_ts"]).dt.normalize()
    elif "trade_date" in df.columns:
        df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.normalize()
    else:
        df["trade_date"] = pd.to_datetime(df.get("timestamp", pd.Timestamp.utcnow())).dt.normalize()

    # compute daily net_pnl per grouping
    daily = (
        df.groupby(["strategy_id", "version", "symbol", "trade_date"])
        .agg(net_pnl=("pnl", "sum"))
        .reset_index()
        .sort_values(["strategy_id", "version", "symbol", "trade_date"])
    )

    targets = []
    for (sid, ver, sym), grp in daily.groupby(["strategy_id", "version", "symbol"]):
        grp = grp.set_index("trade_date").sort_index()
        # compute forward rolling sum
        future_sum = grp["net_pnl"].rolling(window=window_days, min_periods=1).sum().shift(- (window_days - 1))
        # The above approach with shift yields the sum starting at current day covering next window_days.
        # Build rows
        tdf = grp.reset_index()
        tdf[f"target_next_{window_days}d"] = (future_sum.values > 0).astype(int)
        tdf["strategy_id"] = sid; tdf["version"] = ver; tdf["symbol"] = sym
        targets.append(tdf[["strategy_id", "version", "symbol", "trade_date", f"target_next_{window_days}d"]])

    if not targets:
        return pd.DataFrame()

    out = pd.concat(targets, ignore_index=True)
    return out
