# modules/strategies/health/persistent_store.py

import json
import os
from threading import Lock
from typing import Dict

from modules.strategies.health.types import StrategyHealth, StrategyState


class PersistentHealthAdapter:
    """
    Best-effort JSON persistence for strategy health.

    HARD GUARANTEES:
    - Never raises to caller
    - Atomic write (tmp + replace)
    - Corruption-safe (falls back to empty)
    """

    def __init__(self, path: str):
        self._path = path
        self._lock = Lock()

    def load(self) -> Dict[str, StrategyHealth]:
        with self._lock:
            if not os.path.exists(self._path):
                return {}

            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    raw = json.load(f)

                data: Dict[str, StrategyHealth] = {}
                for strategy_id, rec in raw.items():
                    data[strategy_id] = StrategyHealth(
                        state=StrategyState(rec["state"]),
                        failure_count=int(rec["failure_count"]),
                        last_reason=rec.get("last_reason"),
                    )
                return data
            except Exception:
                # Corrupt or unreadable file → safe fallback
                return {}

    def save(self, data: Dict[str, StrategyHealth]) -> None:
        with self._lock:
            try:
                tmp = self._path + ".tmp"
                serializable = {
                    k: {
                        "state": v.state.value,
                        "failure_count": v.failure_count,
                        "last_reason": v.last_reason,
                    }
                    for k, v in data.items()
                }
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(serializable, f)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp, self._path)
            except Exception:
                # Best-effort only
                return
