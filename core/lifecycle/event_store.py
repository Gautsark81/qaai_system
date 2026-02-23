from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import List

from core.lifecycle.contracts.event import LifecycleEvent


class LifecycleEventStore:
    """
    Append-only lifecycle event store (Phase-C).

    Guarantees:
    - Immutable log
    - Deterministic replay
    - Audit-safe
    - Idempotency via natural key:
      (strategy_id, from_state, to_state)
    """

    def __init__(self, path: str | Path):
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: LifecycleEvent) -> None:
        record = self._serialize(event)
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def replay(self) -> List[LifecycleEvent]:
        if not self._path.exists():
            return []

        events: List[LifecycleEvent] = []
        with self._path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    events.append(self._deserialize(json.loads(line)))
        return events

    def replay_for_strategy(self, strategy_id: str) -> List[LifecycleEvent]:
        return [e for e in self.replay() if e.strategy_id == strategy_id]

    def _serialize(self, event: LifecycleEvent) -> dict:
        d = asdict(event)
        d["from_state"] = event.from_state.value
        d["to_state"] = event.to_state.value
        d["reason"] = event.reason.value
        d["as_of"] = event.as_of.isoformat()
        return d

    def _deserialize(self, d: dict) -> LifecycleEvent:
        from core.lifecycle.contracts.state import LifecycleState
        from core.lifecycle.contracts.enums import TransitionReason

        return LifecycleEvent(
            strategy_id=d["strategy_id"],
            from_state=LifecycleState(d["from_state"]),
            to_state=LifecycleState(d["to_state"]),
            reason=TransitionReason(d["reason"]),
            as_of=datetime.fromisoformat(d["as_of"]),
        )
