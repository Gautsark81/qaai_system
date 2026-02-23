# core/operator/operator_memory_store.py
from typing import List
from core.operator.operator_event import OperatorEvent


class OperatorMemoryStore:
    def __init__(self):
        self._events: List[OperatorEvent] = []

    def append(self, event: OperatorEvent) -> None:
        self._events.append(event)

    def all_events(self) -> List[OperatorEvent]:
        return list(self._events)

    def events_for_operator(self, operator_id: str) -> List[OperatorEvent]:
        return [e for e in self._events if e.operator_id == operator_id]
