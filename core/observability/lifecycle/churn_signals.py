from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

from core.lifecycle.contracts.event import LifecycleEvent
from core.lifecycle.contracts.snapshot import LifecycleState


@dataclass(frozen=True)
class LifecycleChurnSignals:
    """
    Read-only observability signals for lifecycle churn / oscillation.

    Purpose:
    - Detect excessive back-and-forth transitions between states
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
        max_allowed_cycles: int,
    ) -> "LifecycleChurnSignals":
        events = sorted(list(events), key=lambda e: e.as_of)
        flags: List[str] = []

        if len(events) < 2:
            return cls(flags=flags)

        # Build sequence of state transitions as pairs (from, to)
        transitions: List[Tuple[LifecycleState, LifecycleState]] = [
            (e.from_state, e.to_state) for e in events
        ]

        # Count oscillation cycles: A->B followed by B->A
        cycles = 0
        for (a_from, a_to), (b_from, b_to) in zip(transitions, transitions[1:]):
            if a_from == b_to and a_to == b_from:
                cycles += 1

        if cycles > max_allowed_cycles:
            flags.append("EXCESSIVE_STATE_CHURN")

        return cls(flags=flags)
