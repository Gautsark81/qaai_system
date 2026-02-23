from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from core.lifecycle.contracts.snapshot import LifecycleState
from core.lifecycle.contracts.event import LifecycleEvent


@dataclass(frozen=True)
class LifecycleOperatorSummary:
    """
    Read-only operator-facing lifecycle summary.

    This object:
    - Aggregates lifecycle events
    - Computes current state
    - Computes time-in-state
    - Attaches observability flags
    - Does NOT make decisions

    IMPORTANT:
    - Must be constructible with partial information
    - recent_transitions is OPTIONAL by design
    """

    strategy_id: str
    current_state: LifecycleState
    days_in_current_state: int
    flags: List[str]

    # Optional for observability / alert payloads
    recent_transitions: List[LifecycleEvent] = field(default_factory=list)

    @staticmethod
    def from_events(
        *,
        strategy_id: str,
        events: List[LifecycleEvent],
        now: datetime,
        stagnation_flags: List[str],
        churn_flags: List[str],
        max_transitions: int = 5,
    ) -> "LifecycleOperatorSummary":
        if not events:
            raise ValueError("LifecycleOperatorSummary requires at least one event")

        # Sort events deterministically
        ordered = sorted(events, key=lambda e: e.as_of)

        latest = ordered[-1]

        # Compute days in current state
        delta = now - latest.as_of
        days_in_state = max(0, delta.days)

        # Combine flags
        combined_flags = list(stagnation_flags) + list(churn_flags)

        return LifecycleOperatorSummary(
            strategy_id=strategy_id,
            current_state=latest.to_state,
            days_in_current_state=days_in_state,
            flags=combined_flags,
            recent_transitions=ordered[-max_transitions:],
        )
