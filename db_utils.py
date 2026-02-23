# qaai_system/db_utils.py
"""
Database utilities for querying Postgres audit tables.
Falls back to JSONL audit logs if DB not available.
"""

import os
import glob
import json
import pandas as pd
import psycopg2

from qaai_system import env_config as cfg


def get_conn():
    """Return a live psycopg2 connection to Postgres."""
    return psycopg2.connect(
        dbname=cfg.POSTGRES_DB,
        user=cfg.POSTGRES_USER,
        password=cfg.POSTGRES_PASSWORD,
        host=cfg.POSTGRES_HOST,
        port=cfg.POSTGRES_PORT,
    )


def fetch_recent_runs(limit: int = 20) -> pd.DataFrame:
    """Fetch recent pipeline runs from Postgres."""
    q = """
    SELECT id, run_timestamp, mode, top_k,
           watchlist, signals, orders
    FROM audit_pipeline_runs
    ORDER BY id DESC
    LIMIT %s
    """
    with get_conn() as conn:
        return pd.read_sql(q, conn, params=[limit])


def fallback_load_audit_logs(audit_dir: str = "audit") -> list[dict]:
    """Fallback: load JSONL audit logs if Postgres is unavailable."""
    files = sorted(
        glob.glob(os.path.join(audit_dir, "pipeline_run_*.jsonl")), reverse=True
    )
    logs = []
    for f in files:
        try:
            with open(f, "r") as fh:
                for line in fh:
                    logs.append(json.loads(line.strip()))
        except Exception as e:
            print(f"Warning: failed to load {f}: {e}")
    return logs
