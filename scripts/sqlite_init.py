# scripts/sqlite_init.py
from infra.sqlite_client import SQLiteClient
from pathlib import Path

SCHEMA = {
    "db/ohlcv.db": """
        CREATE TABLE IF NOT EXISTS ohlcv (
            ts TEXT NOT NULL,
            symbol TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL,
            timeframe TEXT DEFAULT '1d',
            PRIMARY KEY (ts, symbol, timeframe)
        );
    """,
    "db/ticks.db": """
        CREATE TABLE IF NOT EXISTS ticks (
            ts TEXT NOT NULL,
            symbol TEXT NOT NULL,
            price REAL,
            volume REAL,
            bid REAL,
            ask REAL,
            PRIMARY KEY (ts, symbol)
        );
    """,
    "db/features.db": """
        CREATE TABLE IF NOT EXISTS features (
            ts TEXT NOT NULL,
            symbol TEXT NOT NULL,
            feature_key TEXT NOT NULL,
            feature_value REAL,
            PRIMARY KEY (ts, symbol, feature_key)
        );
    """,
    "data/ml_predictions.db": """
        CREATE TABLE IF NOT EXISTS ml_predictions (
            ts TEXT,
            order_id TEXT,
            symbol TEXT,
            side TEXT,
            qty REAL,
            price REAL,
            nav REAL,
            last_price REAL,
            p_fill REAL,
            model_version TEXT,
            outcome_status TEXT
        );
    """,
}


def init():
    for path, ddl in SCHEMA.items():
        print(f"Initializing {path} ...")
        client = SQLiteClient(Path(path))
        client.execute(ddl)
        print(f"✔ Created (or already exists): {path}")


if __name__ == "__main__":
    init()
    print("All DBs initialized.")
