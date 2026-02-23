# modules/execution/idempotency.py

from threading import Lock

class ExecutionLedger:
    def __init__(self):
        self._seen = set()
        self._lock = Lock()

    def register(self, plan_id: str) -> bool:
        with self._lock:
            if plan_id in self._seen:
                return False
            self._seen.add(plan_id)
            return True
