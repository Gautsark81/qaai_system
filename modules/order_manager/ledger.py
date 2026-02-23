# modules/order_manager/ledger.py

import json
import os
from threading import Lock
from typing import Optional


class PlanLedger:
    """
    Persistent idempotency ledger keyed by plan_id.
    Crash-safe via fsync-on-write.
    """

    def __init__(self, path: str):
        self._path = path
        self._lock = Lock()
        self._data = self._load()

    def _load(self) -> dict:
        if not os.path.exists(self._path):
            return {}
        with open(self._path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _flush(self) -> None:
        tmp = self._path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._data, f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self._path)

    def get(self, plan_id: str) -> Optional[str]:
        with self._lock:
            return self._data.get(plan_id)

    def record(self, plan_id: str, broker_order_id: str) -> None:
        with self._lock:
            if plan_id in self._data:
                return
            self._data[plan_id] = broker_order_id
            self._flush()
