from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List, NewType

from modules.portfolio.state import (
    PortfolioSnapshot,
    Position,
)

# -------------------------------------------------------------------
# Domain aliases (must match portfolio.state exactly)
# -------------------------------------------------------------------
Symbol = NewType("Symbol", str)
StrategyId = NewType("StrategyId", str)


class PortfolioSnapshotStore:
    """
    Append-only snapshot persistence.

    Guarantees:
    - Immutable records
    - Deterministic JSONL format
    - Replay-safe reconstruction
    """

    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # File layout
    # ------------------------------------------------------------------
    def _path_for_day(self, ts: datetime) -> Path:
        return self.root / f"snapshots_{ts.date().isoformat()}.jsonl"

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def append(self, snapshot: PortfolioSnapshot) -> None:
        path = self._path_for_day(snapshot.timestamp)
        record = self._serialize(snapshot)

        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, separators=(",", ":")) + "\n")

    def load_all(self) -> List[PortfolioSnapshot]:
        snapshots: List[PortfolioSnapshot] = []

        for file in sorted(self.root.glob("snapshots_*.jsonl")):
            with file.open("r", encoding="utf-8") as f:
                for line in f:
                    snapshots.append(
                        self._deserialize(json.loads(line))
                    )

        return snapshots

    # ------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------
    def _serialize(self, snap: PortfolioSnapshot) -> dict:
        return {
            "timestamp": snap.timestamp.isoformat(),
            "cash": snap.cash,
            "realized_pnl": snap.realized_pnl,
            "metrics": snap.metrics,
            "positions": {
                str(symbol): {
                    "quantity": pos.quantity,
                    "avg_price": pos.avg_price,
                    "strategy_id": str(pos.strategy_id),
                }
                for symbol, pos in snap.positions.items()
            },
        }

    def _deserialize(self, raw: dict) -> PortfolioSnapshot:
        return PortfolioSnapshot(
            timestamp=datetime.fromisoformat(raw["timestamp"]),
            cash=raw["cash"],
            realized_pnl=raw["realized_pnl"],
            metrics=dict(raw.get("metrics", {})),
            positions={
                Symbol(symbol): Position(
                    symbol=Symbol(symbol),
                    quantity=data["quantity"],
                    avg_price=data["avg_price"],
                    strategy_id=StrategyId(data["strategy_id"]),
                )
                for symbol, data in raw["positions"].items()
            },
        )

