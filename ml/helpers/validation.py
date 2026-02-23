"""
Schema and validation helpers for Phase-3.
Includes idempotent migration logic to add missing columns to existing
predictions table so older DBs don't break append writes.
"""

from typing import List
import pandas as pd
import sqlite3


EXPECTED_PRED_COLS = [
    "symbol",
    "timestamp",  # ISO string or pd.Timestamp
    "timeframe",
    "prediction",  # -1/0/1 or probability thresholded
    "probability",  # float 0..1
    "model_version",
]


def validate_predictions_df(df: pd.DataFrame) -> None:
    missing = [c for c in EXPECTED_PRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Predictions DataFrame missing columns: {missing}")
    # types basic checks
    if not pd.api.types.is_numeric_dtype(df["probability"]):
        raise TypeError("probability column must be numeric")
    # timestamp convertible
    try:
        pd.to_datetime(df["timestamp"])
    except Exception as e:
        raise ValueError("timestamp column cannot be parsed as datetime") from e


def _table_columns(conn: sqlite3.Connection, table_name: str) -> List[str]:
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table_name})")
    rows = cur.fetchall()
    # PRAGMA returns: cid, name, type, notnull, dflt_value, pk
    return [r[1] for r in rows]


def ensure_db_schema(conn: sqlite3.Connection) -> None:
    """
    Ensure the SQLite DB has the `predictions` table with required columns.
    If the table exists but is missing columns, add them (ALTER TABLE).
    Safe to call multiple times.
    """
    cur = conn.cursor()

    # If table doesn't exist, create with the full schema.
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='predictions'"
    )
    if not cur.fetchone():
        cur.execute(
            """
            CREATE TABLE predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                prediction REAL NOT NULL,
                probability REAL NOT NULL,
                model_version TEXT,
                created_at TEXT NOT NULL
            );
            """
        )
        conn.commit()
        return

    # Table exists — check columns and add any missing
    existing_cols = _table_columns(conn, "predictions")
    # mapping of desired columns to SQL fragment for ALTER
    desired_columns = {
        "symbol": "TEXT NOT NULL",
        "timestamp": "TEXT NOT NULL",
        "timeframe": "TEXT NOT NULL",
        "prediction": "REAL NOT NULL",
        "probability": "REAL NOT NULL",
        "model_version": "TEXT",
        "created_at": "TEXT NOT NULL",
    }

    for col, col_type in desired_columns.items():
        if col not in existing_cols:
            # ALTER TABLE ADD COLUMN is safe to run multiple times for different columns.
            sql = f"ALTER TABLE predictions ADD COLUMN {col} {col_type}"
            cur.execute(sql)
    conn.commit()
