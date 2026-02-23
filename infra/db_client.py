# File: infra/db_client.py

import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

load_dotenv()


class DBClient:
    def __init__(self, autoconnect: bool = True):
        """
        Database client wrapper for PostgreSQL.

        :param autoconnect: If True (default), connect immediately.
                            If False or MOCK_DB=1, connection is skipped
                            until explicitly required.
        """
        self.conn = None
        self.mock_mode = os.getenv("MOCK_DB", "0") == "1"

        if autoconnect and not self.mock_mode:
            self._connect()

    def _connect(self):
        """Establish a database connection unless in MOCK_DB mode."""
        if self.mock_mode:
            return None
        try:
            self.conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME", "qaai_db"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "432156"),
                host=os.getenv("DB_HOST", "localhost"),
                port=os.getenv("DB_PORT", 5432),
            )
        except Exception as e:
            raise RuntimeError(f"[DB CONNECTION ERROR] {e}")

    def _ensure_conn(self):
        """Reconnect if connection is missing or closed."""
        if self.mock_mode:
            return False
        if self.conn is None or self.conn.closed != 0:
            self._connect()
        return True

    # ------------------------------------------------------------------
    # Data operations
    # ------------------------------------------------------------------
    def insert_ohlcv(self, df, symbol):
        if self.mock_mode or df.empty:
            return

        records = [
            (
                symbol,
                row["date"],
                row["open"],
                row["high"],
                row["low"],
                row["close"],
                row["volume"],
            )
            for _, row in df.iterrows()
        ]

        insert_query = """
            INSERT INTO ohlcv_data (symbol, date, open, high, low, close, volume)
            VALUES %s
            ON CONFLICT (symbol, date)
            DO UPDATE SET
              open = EXCLUDED.open,
              high = EXCLUDED.high,
              low = EXCLUDED.low,
              close = EXCLUDED.close,
              volume = EXCLUDED.volume;
        """

        try:
            if not self._ensure_conn():
                return
            with self.conn.cursor() as cur:
                execute_values(cur, insert_query, records)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"[DB INSERT ERROR] {e}")

    def fetch_watchlist(self):
        if self.mock_mode:
            # ✅ Return a non-empty dummy watchlist in mock mode for tests
            return ["AAPL", "GOOG", "MSFT"]

        query = "SELECT symbol FROM watchlist WHERE active = TRUE;"
        try:
            self._ensure_conn()
            with self.conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
                return [row[0] for row in rows]
        except Exception as e:
            raise RuntimeError(f"[FETCH WATCHLIST ERROR] {e}")

    def fetch_ohlcv(self, symbol, timeframe="5min", limit=500):
        """
        Fetch OHLCV data by timeframe and limit.
        If timeframe is not used in your DB schema, it can be used to choose
        which table or view to query.
        """
        if self.mock_mode:
            return pd.DataFrame()

        table_name = "ohlcv_data"
        query = f"""
            SELECT date, open, high, low, close, volume
            FROM {table_name}
            WHERE symbol = %s
            ORDER BY date DESC
            LIMIT %s;
        """

        try:
            self._ensure_conn()
            with self.conn.cursor() as cur:
                cur.execute(query, (symbol, limit))
                rows = cur.fetchall()
                if not rows:
                    return pd.DataFrame()
                df = pd.DataFrame(
                    rows,
                    columns=["timestamp", "open", "high", "low", "close", "volume"],
                )
                df.set_index("timestamp", inplace=True)
                df.sort_index(inplace=True)
                return df
        except Exception as e:
            raise RuntimeError(f"[FETCH OHLCV ERROR] {e}")

    def write_screener_scores(self, results_df):
        if self.mock_mode or results_df.empty:
            return

        insert_query = """
            INSERT INTO screener_results (symbol, passed, timestamp)
            VALUES %s
            ON CONFLICT (symbol, timestamp)
            DO UPDATE SET passed = EXCLUDED.passed;
        """

        timestamp = datetime.now()
        values = [
            (row["symbol"], row["passed"], timestamp)
            for _, row in results_df.iterrows()
        ]

        try:
            self._ensure_conn()
            with self.conn.cursor() as cur:
                execute_values(cur, insert_query, values)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"[DB WRITE SCREENER ERROR] {e}")

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
