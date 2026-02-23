# qaai_system/db/database.py
import sqlite3
from pathlib import Path

DB_PATH = Path("data_store/qaai.db")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def initialize_db():
    with get_connection() as conn:
        cursor = conn.cursor()

        # OHLCV Table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ohlcv (
                symbol TEXT,
                date TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                PRIMARY KEY (symbol, date)
            )
        """
        )

        # Watchlist Table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS watchlist (
                symbol TEXT PRIMARY KEY,
                added_on TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Symbol Metadata
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS symbol_metadata (
                symbol TEXT PRIMARY KEY,
                sector TEXT,
                industry TEXT,
                exchange TEXT
            )
        """
        )

        conn.commit()
        print("[DB INIT] All tables initialized.")
