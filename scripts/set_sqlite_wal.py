# scripts/set_sqlite_wal.py
from infra.sqlite_client import SQLiteClient
from pathlib import Path

db_paths = [
    Path("db/ohlcv.db"),
    Path("db/ticks.db"),
    Path("db/features.db"),
    Path("db/audit.db"),
    Path("data/ml_predictions.db"),
]

for p in db_paths:
    client = SQLiteClient(p)
    # Use the client's connection to set WAL. SQLiteClient.connect() returns sqlite3.Connection
    conn = client.connect()
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA journal_mode;")
        res = cur.fetchone()
        print(f"{p}: journal_mode -> {res[0] if res else 'unknown'}")
        conn.commit()
    finally:
        conn.close()
