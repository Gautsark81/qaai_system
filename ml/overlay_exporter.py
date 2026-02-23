"""
Overlay exporter: merge raw signals (optional) and predictions; output parquet with same partitioning.
If raw_signals_path is provided (parquet), it will be joined on symbol+timestamp.
"""

from pathlib import Path
import pandas as pd
from typing import Optional
from ml.helpers.parquet_utils import (
    atomic_to_parquet,
    ensure_parquet_engine_installed_msg,
)


def read_raw_signals(parquet_path: str) -> pd.DataFrame:
    return pd.read_parquet(parquet_path)


def merge_predictions_and_signals(
    preds: pd.DataFrame, raw_signals: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Left-join raw_signals onto preds by symbol and timestamp (exact match).
    If raw_signals is None, return preds with an empty 'raw_signal' column.
    """
    df = preds.copy()
    if raw_signals is None:
        df["raw_signal"] = pd.NA
        return df
    # normalize timestamp dtype
    raw_signals = raw_signals.copy()
    if "timestamp" in raw_signals.columns:
        raw_signals["timestamp"] = pd.to_datetime(raw_signals["timestamp"])
    # perform join
    merged = df.merge(
        raw_signals, on=["symbol", "timestamp"], how="left", suffixes=("", "_raw")
    )
    return merged


def export_overlay(
    preds_df: pd.DataFrame, out_dir: str, raw_signals_path: Optional[str] = None
) -> dict:
    msg = ensure_parquet_engine_installed_msg()
    if msg:
        raise RuntimeError(msg)

    raw = None
    if raw_signals_path:
        raw = read_raw_signals(raw_signals_path)

    merged = merge_predictions_and_signals(preds_df, raw)
    # add date col
    merged = merged.copy()
    merged["date"] = merged["timestamp"].dt.strftime("%Y-%m-%d")
    out_dir = Path(out_dir)
    partition_cols = ["symbol", "date", "timeframe"]
    atomic_to_parquet(merged, out_dir, partition_cols=partition_cols)
    files_written = sum(1 for _ in out_dir.rglob("*.parquet"))
    return {"rows": len(merged), "files_written": files_written}
