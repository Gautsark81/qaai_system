from __future__ import annotations

import json
import os
import threading
from typing import Dict, Iterator, Any


class ExecutionJournal:
    """
    Append-only, crash-safe execution journal.

    Guarantees:
    - Atomic append
    - fsync durability
    - Replay ignores partial / corrupt trailing lines
    - Deterministic iteration order
    - Exactly-once key detection
    """

    def __init__(self, path: str):
        self.path = path
        self._lock = threading.Lock()

        # Ensure directory exists (safe even if dirname is empty)
        directory = os.path.dirname(self.path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        # Touch file if missing
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8"):
                pass

    # ==========================================================
    # Append
    # ==========================================================
    def append(self, record: Dict[str, Any]) -> None:
        """
        Atomically append a single JSON record.

        Contract:
        - One record per line
        - fsync ensures durability
        - Never mutates existing data
        """
        if not isinstance(record, dict):
            raise TypeError("ExecutionJournal only accepts dict records")

        line = json.dumps(record, separators=(",", ":")) + "\n"

        with self._lock:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(line)
                f.flush()
                os.fsync(f.fileno())

    # ==========================================================
    # Replay
    # ==========================================================
    def replay(self) -> Iterator[Dict[str, Any]]:
        """
        Replay journal records in deterministic order.

        Rules:
        - Line-by-line
        - Ignore empty lines
        - Stop at first partial / invalid JSON line
        - Never raise during replay
        """
        if not os.path.exists(self.path):
            return

        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    # 🔒 CRITICAL:
                    # Partial write → crash mid-line → stop replay
                    break

                if isinstance(obj, dict):
                    yield obj

    # ==========================================================
    # Exactly-once fence
    # ==========================================================
    def has_seen(self, key: str) -> bool:
        """
        Check if a record with the given key was already committed.

        Used for exactly-once semantics (fills, PnL, etc).
        """
        if not key or not os.path.exists(self.path):
            return False

        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    # Ignore tail corruption
                    break

                if rec.get("key") == key:
                    return True

        return False
