# clients/sqlite_order_cache.py
"""
SQLite-backed order cache.

Persists order metadata (JSON) keyed by order_id so OrderManager can reload local cache on restart.

API:
- save_order(order_id: str, metadata: dict)
- load_all() -> dict(order_id -> metadata)
- delete_order(order_id)
- close()
"""

from __future__ import annotations
import sqlite3
import json
import threading
from typing import Dict, Any, Optional

class SqliteOrderCache:
    def __init__(self, path: str = ":memory:"):
        self._path = path
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self._path, check_same_thread=False)
        self._init_table()

    def _init_table(self):
        cur = self._conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                value TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self._conn.commit()

    def save_order(self, order_id: str, metadata: Dict[str, Any]) -> None:
        text = json.dumps(metadata)
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("INSERT OR REPLACE INTO orders (order_id, value) VALUES (?, ?)", (order_id, text))
            self._conn.commit()

    def load_all(self) -> Dict[str, Dict[str, Any]]:
        out: Dict[str, Dict[str, Any]] = {}
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("SELECT order_id, value FROM orders")
            rows = cur.fetchall()
        for oid, txt in rows:
            try:
                out[oid] = json.loads(txt)
            except Exception:
                out[oid] = {"raw": txt}
        return out

    def delete_order(self, order_id: str) -> None:
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
            self._conn.commit()

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass
