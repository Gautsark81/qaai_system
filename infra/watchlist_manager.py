# infra/watchlist_manager.py
from infra import db_client

WATCHLIST_TABLE = "watchlist"


class WatchlistManager:
    def __init__(self):
        self.conn = db_client.get_db_connection()
        self._ensure_table()

    def _ensure_table(self):
        with self.conn.cursor() as cur:
            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {WATCHLIST_TABLE} (
                    id SERIAL PRIMARY KEY,
                    symbol TEXT NOT NULL UNIQUE,
                    name TEXT,
                    added_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
            )
            self.conn.commit()

    def add_symbol(self, symbol: str, name: str = None):
        with self.conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {WATCHLIST_TABLE} (symbol, name)
                VALUES (%s, %s)
                ON CONFLICT(symbol) DO NOTHING;
            """,
                (symbol.upper(), name),
            )
            self.conn.commit()

    def remove_symbol(self, symbol: str):
        with self.conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {WATCHLIST_TABLE} WHERE symbol = %s;", (symbol.upper(),)
            )
            self.conn.commit()

    def get_watchlist(self):
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT symbol, name FROM {WATCHLIST_TABLE} ORDER BY symbol;")
            return cur.fetchall()

    def clear_all(self):
        with self.conn.cursor() as cur:
            cur.execute(f"DELETE FROM {WATCHLIST_TABLE};")
            self.conn.commit()
