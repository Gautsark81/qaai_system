# core/explainability/timeline/timeline.py
from typing import Iterable, List
from core.explainability.timeline.events import NarrativeEvent


class NarrativeTimeline:
    """
    Builds a deterministic, append-only narrative timeline.
    """

    def __init__(self, events: Iterable[NarrativeEvent]):
        # Deterministic ordering by timestamp then category
        self._events: List[NarrativeEvent] = sorted(
            list(events),
            key=lambda e: (e.timestamp, e.category),
        )

    def all_events(self) -> List[NarrativeEvent]:
        return list(self._events)

    def filter_by_category(self, category: str) -> List[NarrativeEvent]:
        return [e for e in self._events if e.category == category]
