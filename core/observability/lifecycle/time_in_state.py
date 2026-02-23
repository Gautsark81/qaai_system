# core/observability/lifecycle/time_in_state.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Iterable, Optional

from core.lifecycle.contracts.snapshot import LifecycleState
from core.lifecycle.contracts.event import LifecycleEvent


@dataclass(frozen=True)
class LifecycleTimeInStateReport:
    duration_by_state: Dict[LifecycleState, timedelta]
    first_event_at: datetime
    last_event_at: datetime

    @classmethod
    def from_events(
        cls,
        events: Iterable[LifecycleEvent],
        *,
        as_of: Optional[datetime] = None,
    ) -> "LifecycleTimeInStateReport":

        events = sorted(events, key=lambda e: e.as_of)

        if not events:
            return cls(
                duration_by_state={},
                first_event_at=datetime.min,
                last_event_at=datetime.min,
            )

        duration_by_state: Dict[LifecycleState, timedelta] = {}

        first_event_at = events[0].as_of
        last_event_at = events[-1].as_of

        # If no reference time provided, use last event time
        reference_time = as_of or last_event_at

        for i in range(len(events)):
            current_event = events[i]
            current_state = current_event.from_state
            current_time = current_event.as_of

            if i + 1 < len(events):
                next_time = events[i + 1].as_of
            else:
                next_time = reference_time

            delta = next_time - current_time

            duration_by_state[current_state] = (
                duration_by_state.get(current_state, timedelta())
                + delta
            )

        return cls(
            duration_by_state=duration_by_state,
            first_event_at=first_event_at,
            last_event_at=last_event_at,
        )
