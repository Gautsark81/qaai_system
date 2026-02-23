#!/usr/bin/env python3
"""
Apply SQL migrations found in db/migrations in ordinal order.
Each migration file should be idempotent or rely on sqlite's IF NOT EXISTS patterns.
"""
import sqlite3
from pathlib import Path

BASE = Path.cwd()
MIGRATIONS_DIR = BASE / "db" / "migrations"
DBS = [
    BASE / "db" / "ohlcv.db",
    BASE / "db" / "ticks.db",
    BASE / "db" / "features.db",
    BASE / "data" / "ml_predictions.db",
]


def apply_migration(db_path: Path, sql_text: str, name: str):
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.executescript(sql_text)
        conn.commit()
        print(f"Applied migration {name} to {db_path}")
    finally:
        conn.close()


def main():
    if not MIGRATIONS_DIR.exists():
        print("No migrations folder; skipping.")
        return
    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not files:
        print("No migration files found.")
        return
    for f in files:
        sql = f.read_text()
        for db in DBS:
            apply_migration(db, sql, f.name)


if __name__ == "__main__":
    main()
