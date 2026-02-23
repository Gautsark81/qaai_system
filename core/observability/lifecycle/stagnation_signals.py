from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List
from datetime import datetime, timedelta

from core.lifecycle.contracts.event import LifecycleEvent
from core.lifecycle.contracts.snapshot import LifecycleState


@dataclass(frozen=True)
class LifecycleStagnationSignals:
    """
    Read-only observability signals for lifecycle stagnation.

    Purpose:
    - Detect excessive time spent in a lifecycle state
    - Emit governance / alerting signals ONLY
    - No lifecycle logic
    - No mutation
    - Deterministic and event-driven
    """

    flags: List[str]

    @classmethod
    def from_events(
        cls,
        *,
        events: Iterable[LifecycleEvent],
        now: datetime,
        max_days_in_state: Dict[LifecycleState, int],
    ) -> "LifecycleStagnationSignals":
        events = sorted(list(events), key=lambda e: e.as_of)

        flags: List[str] = []

        if not events:
            return cls(flags=flags)

        # Current lifecycle state is the last transition's to_state
        last_event = events[-1]
        current_state = last_event.to_state
        days_in_state = (now - last_event.as_of).days

        limit = max_days_in_state.get(current_state)

        if limit is not None and days_in_state > limit:
            flags.append(f"STAGNANT_IN_{current_state.value}")

        return cls(flags=flags)
