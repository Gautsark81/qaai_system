from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable
from collections import Counter
from datetime import datetime

from core.lifecycle.contracts.event import LifecycleEvent
from core.lifecycle.contracts.snapshot import LifecycleState
from core.lifecycle.contracts.enums import TransitionReason


@dataclass(frozen=True)
class LifecycleTransitionDensity:
    """
    Read-only aggregation of lifecycle transition frequency.

    Purpose:
    - Quantify how often lifecycle transitions occur
    - Support observability, governance, and audit
    - NO mutation
    - NO lifecycle logic
    """

    total_transitions: int
    by_state: Dict[LifecycleState, int]
    by_reason: Dict[TransitionReason, int]
    first_event_at: datetime
    last_event_at: datetime

    @classmethod
    def from_events(
        cls,
        events: Iterable[LifecycleEvent],
    ) -> "LifecycleTransitionDensity":
        events = list(events)

        if not events:
            return cls(
                total_transitions=0,
                by_state={},
                by_reason={},
                first_event_at=None,
                last_event_at=None,
            )

        state_counter = Counter()
        reason_counter = Counter()

        for event in events:
            state_counter[event.from_state] += 1
            reason_counter[event.reason] += 1

        ordered = sorted(events, key=lambda e: e.as_of)

        return cls(
            total_transitions=len(events),
            by_state=dict(state_counter),
            by_reason=dict(reason_counter),
            first_event_at=ordered[0].as_of,
            last_event_at=ordered[-1].as_of,
        )
