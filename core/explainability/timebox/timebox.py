# core/explainability/timebox/timebox.py
from typing import Iterable, List
from core.explainability.timeline.events import NarrativeEvent


class TimeBoxedExplanation:
    """
    Packages narrative events within a specific time window.

    NOTE:
    - No recomputation
    - No inference
    - Deterministic filtering only
    """

    def __init__(
        self,
        *,
        events: Iterable[NarrativeEvent],
        start_time: str,
        end_time: str,
    ):
        self.start_time = start_time
        self.end_time = end_time

        # Deterministic filter + ordering
        self._events: List[NarrativeEvent] = sorted(
            [
                e
                for e in events
                if self.start_time <= e.timestamp <= self.end_time
            ],
            key=lambda e: (e.timestamp, e.category),
        )

    def events(self) -> List[NarrativeEvent]:
        return list(self._events)
