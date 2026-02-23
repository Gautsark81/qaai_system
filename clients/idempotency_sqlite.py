# clients/idempotency_sqlite.py
from __future__ import annotations
import sqlite3
import json
import threading
from typing import Optional, Dict, Any

class SqliteIdempotencyStore:
    def __init__(self, path: str = ":memory:"):
        self._path = path
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self._path, check_same_thread=False)
        self._init_table()

    def _init_table(self):
        cur = self._conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS idempotency (key TEXT PRIMARY KEY, value TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
        )
        self._conn.commit()

    def __contains__(self, key: str) -> bool:
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("SELECT 1 FROM idempotency WHERE key = ? LIMIT 1", (key,))
            return cur.fetchone() is not None

    def __getitem__(self, key: str) -> Dict[str, Any]:
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("SELECT value FROM idempotency WHERE key = ? LIMIT 1", (key,))
            row = cur.fetchone()
            if not row:
                raise KeyError(key)
            return json.loads(row[0])

    def __setitem__(self, key: str, value: Dict[str, Any]) -> None:
        text = json.dumps(value)
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("INSERT OR REPLACE INTO idempotency (key, value) VALUES (?, ?)", (key, text))
            self._conn.commit()

    def get(self, key: str, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def keys(self):
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("SELECT key FROM idempotency")
            rows = cur.fetchall()
            return [r[0] for r in rows]

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass
