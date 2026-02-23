# path: qaai_system/portfolio/snapshot_store.py
from __future__ import annotations

"""
SnapshotStore — minimal JSONL-based persistence for portfolio snapshots.

Usage:
    store = SnapshotStore(path="logs/portfolio_snapshots.jsonl")
    snap = tracker.get_portfolio_snapshot(equity=..., cash=...)
    store.append_snapshot(snap)

    last_10 = store.load_last_n(10)
"""

import json
import os
from dataclasses import asdict
from typing import Iterable, List, Optional

from .models import PortfolioSnapshot


class SnapshotStore:
    def __init__(self, path: str) -> None:
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    def append_snapshot(self, snapshot: PortfolioSnapshot) -> None:
        """
        Append a snapshot as a single JSONL line.

        This is best-effort only; any I/O error is swallowed to avoid
        impacting the trading loop.
        """
        try:
            payload = asdict(snapshot)
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(payload) + "\n")
        except Exception:
            # Never break the trading loop due to logging
            pass

    def load_last_n(self, n: int = 100) -> List[Dict[str, Any]]:
        """
        Load the last N snapshots from the JSONL file, newest last.
        """
        if not os.path.exists(self.path):
            return []

        lines: List[str] = []
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception:
            return []

        selected = lines[-n:]
        out: List[Dict[str, Any]] = []
        for line in selected:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
        return out

    def load_latest(self) -> Optional[Dict[str, Any]]:
        """
        Load the single latest snapshot (if any).
        """
        last = self.load_last_n(1)
        return last[0] if last else None
