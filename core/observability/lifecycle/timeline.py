from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from core.lifecycle.contracts.event import LifecycleEvent


@dataclass(frozen=True)
class LifecycleAuditTimeline:
    """
    Immutable, read-only audit timeline for lifecycle events.

    Purpose:
    - Provide a deterministic, chronologically ordered view
      of lifecycle transitions for observability and audit.
    - NO lifecycle logic.
    - NO mutation.
    """

    _events: List[LifecycleEvent]

    def __init__(self, events: Iterable[LifecycleEvent]):
        # Defensive copy + deterministic ordering
        ordered = sorted(
            list(events),
            key=lambda e: e.as_of,
        )
        object.__setattr__(self, "_events", ordered)

    @property
    def events(self) -> List[LifecycleEvent]:
        """
        Chronologically ordered lifecycle events.
        """
        return list(self._events)
