# modules/execution/idempotent_order_manager.py
from __future__ import annotations
import sqlite3
import json
import hashlib
import threading
import time
from typing import Callable, Dict, Any, Optional


class IdempotentOrderManager:
    """
    Idempotent order manager backed by sqlite for deduplication.

    - order_sender: Callable[[order_payload: Dict], Dict] -> the downstream function that actually sends orders
    - dbpath: sqlite path; use ':memory:' for ephemeral
    """

    def __init__(self, order_sender: Callable[[Dict[str, Any]], Dict[str, Any]], dbpath: str = ":memory:"):
        self.sender = order_sender
        self.dbpath = dbpath
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        with self._conn() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS orders (id TEXT PRIMARY KEY, payload TEXT, status TEXT, response TEXT, created_at REAL)"
            )
            conn.commit()

    def _conn(self):
        # use short timeout for concurrency safety
        return sqlite3.connect(self.dbpath, timeout=5.0, check_same_thread=False)

    @staticmethod
    def _hash_payload(payload: Dict[str, Any]) -> str:
        # create deterministic id (use sorted JSON)
        text = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def send_order(self, payload: Dict[str, Any], retry_on_conflict: bool = True, max_retries: int = 3, retry_delay: float = 0.5) -> Dict[str, Any]:
        """
        Send an order idempotently.
        - If payload hash exists and status == 'done' -> returns saved response
        - If exists and status == 'pending' -> waits (or returns pending marker)
        - Otherwise inserts pending row and attempts to send via sender
        """
        oid = self._hash_payload(payload)

        with self._lock:
            conn = self._conn()
            cur = conn.cursor()
            row = cur.execute("SELECT id, status, response FROM orders WHERE id = ?", (oid,)).fetchone()
            if row:
                _id, status, response = row
                if status == "done":
                    conn.close()
                    return json.loads(response)
                if status == "pending":
                    # a concurrent in-flight order exists; wait for completion (poll)
                    conn.close()
                    if retry_on_conflict:
                        for i in range(max_retries):
                            time.sleep(retry_delay)
                            with self._conn() as c2:
                                r2 = c2.execute("SELECT status, response FROM orders WHERE id = ?", (oid,)).fetchone()
                                if r2 and r2[0] == "done":
                                    return json.loads(r2[1])
                        raise RuntimeError("Order still pending after retries")
                    else:
                        raise RuntimeError("Order pending")
            # insert pending row
            cur.execute("INSERT OR REPLACE INTO orders (id, payload, status, response, created_at) VALUES (?, ?, ?, ?, ?)",
                        (oid, json.dumps(payload, ensure_ascii=False), "pending", json.dumps({}), time.time()))
            conn.commit()
            conn.close()

        # attempt to send (outside lock to avoid blocking others)
        attempt = 0
        last_exc = None
        while attempt < max_retries:
            try:
                resp = self.sender(payload)
                # write done
                with self._conn() as c:
                    c.execute("UPDATE orders SET status = ?, response = ? WHERE id = ?", ("done", json.dumps(resp, ensure_ascii=False), oid))
                    c.commit()
                return resp
            except Exception as e:
                last_exc = e
                attempt += 1
                time.sleep(retry_delay)

        # mark failed
        with self._conn() as c:
            c.execute("UPDATE orders SET status = ?, response = ? WHERE id = ?", ("failed", json.dumps({"error": str(last_exc)}), oid))
            c.commit()
        raise last_exc
