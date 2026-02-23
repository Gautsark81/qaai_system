from typing import List

from .models import ThrottleDecisionEvent


class ThrottleAuditLedger:
    """
    Deterministic append-only ledger.
    """

    def __init__(self) -> None:
        self._events: List[ThrottleDecisionEvent] = []

    def append(self, event: ThrottleDecisionEvent) -> None:
        self._events.append(event)

    @property
    def events(self) -> List[ThrottleDecisionEvent]:
        return list(self._events)

    def by_strategy(self, strategy_id: str):
        return [e for e in self._events if e.strategy_id == strategy_id]