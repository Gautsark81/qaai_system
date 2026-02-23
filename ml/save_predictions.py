"""
Save predictions to SQLite and write a small metadata summary.
"""

import sqlite3
import pandas as pd
import json
from datetime import datetime
from typing import Optional
from ml.helpers.validation import validate_predictions_df, ensure_db_schema


def save_predictions_df(
    df: pd.DataFrame, db_path: str, meta_out: Optional[str] = None
) -> None:
    """
    Validate DataFrame and append to SQLite predictions table.
    """
    validate_predictions_df(df)
    # normalize timestamp column to ISO
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime("%Y-%m-%dT%H:%M:%S%z")
    df["created_at"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    # keep only expected columns + created_at
    cols = [
        "symbol",
        "timestamp",
        "timeframe",
        "prediction",
        "probability",
        "model_version",
        "created_at",
    ]
    df = df[cols]

    conn = sqlite3.connect(db_path, timeout=30)
    try:
        ensure_db_schema(conn)
        df.to_sql("predictions", conn, if_exists="append", index=False)
    finally:
        conn.close()

    # write metadata file if requested
    if meta_out:
        meta = {
            "rows_written": len(df),
            "symbols": sorted(df["symbol"].unique().tolist()),
            "timeframe": sorted(df["timeframe"].unique().tolist()),
            "model_version": sorted(df["model_version"].dropna().unique().tolist()),
            "written_at_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        with open(meta_out, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)


def read_predictions_count(db_path: str) -> int:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM predictions")
        return cur.fetchone()[0]
    finally:
        conn.close()
