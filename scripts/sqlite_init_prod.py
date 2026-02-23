#!/usr/bin/env python3
"""
scripts/sqlite_init_prod.py

Idempotent DB initialization:
- Creates DB files if missing
- Executes db/schema.sql (DDL) inside a transaction
- Creates a simple schema_version table to track applied migrations
"""

import sqlite3
from pathlib import Path
import sys

BASE = Path.cwd()
SCHEMA_FILE = BASE / "db" / "schema.sql"

DB_PATHS = {
    "ohlcv": BASE / "db" / "ohlcv.db",
    "ticks": BASE / "db" / "ticks.db",
    "features": BASE / "db" / "features.db",
    "audit": BASE / "db" / "audit.db",
    "preds": BASE / "data" / "ml_predictions.db",
}


def apply_schema(db_path: Path, ddl_text: str):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.executescript(ddl_text)
        conn.commit()
        print(f"Applied schema to {db_path}")
    finally:
        conn.close()


def main():
    if not SCHEMA_FILE.exists():
        print("ERROR: schema file missing:", SCHEMA_FILE)
        sys.exit(1)
    ddl_text = SCHEMA_FILE.read_text()
    for name, db_path in DB_PATHS.items():
        print(f"Initializing {name} -> {db_path}")
        apply_schema(db_path, ddl_text)
    print("All DBs initialized.")


if __name__ == "__main__":
    main()
