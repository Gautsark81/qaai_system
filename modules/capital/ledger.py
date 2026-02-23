from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Literal, Optional
import json
import os
from pathlib import Path


LedgerEventType = Literal[
    "INIT",
    "RESERVE",
    "RELEASE",
    "ALLOCATE",
    "DEALLOCATE",
]


@dataclass(frozen=True)
class LedgerEvent:
    type: LedgerEventType
    amount: float
    strategy_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "amount": self.amount,
            "strategy_id": self.strategy_id,
        }

    @staticmethod
    def from_dict(d: dict) -> "LedgerEvent":
        return LedgerEvent(
            type=d["type"],
            amount=float(d["amount"]),
            strategy_id=d.get("strategy_id"),
        )


class CapitalLedger:
    """
    Authoritative capital ledger.

    Append-only journal.
    Deterministic replay.
    Restart-safe.
    """

    def __init__(self, journal_path: Path):
        self._journal_path = Path(journal_path)
        self._events: List[LedgerEvent] = []

        self._total: float = 0.0
        self._reserved: float = 0.0
        self._allocations: Dict[str, float] = {}

        if self._journal_path.exists():
            self._load()

    # ---------- Public API ----------

    def initialize(self, total_capital: float) -> None:
        if self._events:
            raise RuntimeError("Ledger already initialized")

        if total_capital <= 0:
            raise ValueError("Total capital must be positive")

        self._append(LedgerEvent("INIT", total_capital))

    def reserve(self, amount: float) -> None:
        self._require_positive(amount)
        self._require_free(amount)
        self._append(LedgerEvent("RESERVE", amount))

    def release(self, amount: float) -> None:
        self._require_positive(amount)
        if amount > self._reserved:
            raise ValueError("Cannot release more than reserved")
        self._append(LedgerEvent("RELEASE", amount))

    def allocate(self, strategy_id: str, amount: float) -> None:
        self._require_positive(amount)
        self._require_free(amount)
        self._append(LedgerEvent("ALLOCATE", amount, strategy_id))

    def deallocate(self, strategy_id: str, amount: float) -> None:
        self._require_positive(amount)
        current = self._allocations.get(strategy_id, 0.0)
        if amount > current:
            raise ValueError("Cannot deallocate more than allocated")
        self._append(LedgerEvent("DEALLOCATE", amount, strategy_id))

    # ---------- Read-only views ----------

    @property
    def total_capital(self) -> float:
        return self._total

    @property
    def reserved_capital(self) -> float:
        return self._reserved

    @property
    def free_capital(self) -> float:
        return self._total - self._reserved - sum(self._allocations.values())

    def allocation_for(self, strategy_id: str) -> float:
        return self._allocations.get(strategy_id, 0.0)

    def allocations(self) -> Dict[str, float]:
        return dict(self._allocations)

    # ---------- Internal ----------

    def _append(self, event: LedgerEvent) -> None:
        self._apply(event)
        self._events.append(event)
        self._persist_event(event)

    def _apply(self, event: LedgerEvent) -> None:
        if event.type == "INIT":
            self._total = event.amount

        elif event.type == "RESERVE":
            self._reserved += event.amount

        elif event.type == "RELEASE":
            self._reserved -= event.amount

        elif event.type == "ALLOCATE":
            sid = event.strategy_id
            self._allocations[sid] = self._allocations.get(sid, 0.0) + event.amount

        elif event.type == "DEALLOCATE":
            sid = event.strategy_id
            self._allocations[sid] -= event.amount
            if self._allocations[sid] == 0.0:
                del self._allocations[sid]

        self._assert_invariants()

    def _assert_invariants(self) -> None:
        if self._total < 0:
            raise AssertionError("Total capital negative")

        if self._reserved < 0:
            raise AssertionError("Reserved capital negative")

        if self.free_capital < -1e-9:
            raise AssertionError("Free capital negative")

    def _persist_event(self, event: LedgerEvent) -> None:
        self._journal_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._journal_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event.to_dict()) + "\n")

    def _load(self) -> None:
        with open(self._journal_path, "r", encoding="utf-8") as f:
            for line in f:
                event = LedgerEvent.from_dict(json.loads(line))
                self._apply(event)
                self._events.append(event)

    @staticmethod
    def _require_positive(amount: float) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive")

    def _require_free(self, amount: float) -> None:
        if amount > self.free_capital:
            raise ValueError("Insufficient free capital")
