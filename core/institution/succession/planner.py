# core/institution/succession/planner.py
from typing import List
from core.institution.succession.models import Steward, SuccessionEvent


class SuccessionPlanner:
    """
    Records and governs stewardship succession.

    HARD RULE:
    - Succession must be explicit and auditable.
    """

    def __init__(self, *, initial_steward: Steward):
        self._current = initial_steward
        self._history: List[SuccessionEvent] = []

    def current_steward(self) -> Steward:
        return self._current

    def history(self) -> List[SuccessionEvent]:
        return list(self._history)

    def handover(self, *, to_steward: Steward, reason: str) -> SuccessionEvent:
        event = SuccessionEvent(
            from_steward=self._current,
            to_steward=to_steward,
            reason=reason,
        )
        self._history.append(event)
        self._current = to_steward
        return event
