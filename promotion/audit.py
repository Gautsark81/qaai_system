# promotion/audit.py
"""
Simple append-only JSONL audit writer for promotion decisions.
Each line is a JSON dict with keys:
    ts_iso, strategy_id, decision, reason, rule (optional), metrics
"""

from __future__ import annotations
import json
import os
import time
from typing import Dict, Any, Iterable, Optional, List
from datetime import datetime

# Naive file lock for concurrency (POSIX-friendly fallback)
try:
    import fcntl  # type: ignore
except Exception:
    fcntl = None  # Windows will not have fcntl; write is still atomic for append on many FS

def _safe_open(path: str, mode: str = "a"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, mode, encoding="utf-8")

class AuditWriter:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def append(self, record: Dict[str, Any]) -> None:
        rec = dict(record)
        rec.setdefault("ts_iso", datetime.utcnow().isoformat() + "Z")
        line = json.dumps(rec, default=str, ensure_ascii=False)
        # append atomically
        f = _safe_open(self.filepath, "a")
        try:
            if fcntl:
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                except Exception:
                    pass
            f.write(line + "\n")
            f.flush()
            os.fsync(f.fileno())
        finally:
            try:
                if fcntl:
                    try:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    except Exception:
                        pass
            except Exception:
                pass
            f.close()

    def read_all(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.filepath):
            return []
        outs = []
        with open(self.filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    outs.append(json.loads(line))
                except Exception:
                    # skip malformed line
                    continue
        return outs

    def query(self, strategy_id: Optional[str] = None) -> List[Dict[str, Any]]:
        recs = self.read_all()
        if strategy_id is None:
            return recs
        return [r for r in recs if r.get("strategy_id") == strategy_id]
