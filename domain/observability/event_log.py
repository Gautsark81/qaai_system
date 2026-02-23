from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class SystemEvent:
    ts: datetime
    level: str       # INFO / WARN / ERROR
    source: str
    message: str


class EventLog:
    def __init__(self):
        self._events: List[SystemEvent] = []

    def record(self, event: SystemEvent) -> None:
        self._events.append(event)

    def all(self) -> List[SystemEvent]:
        return list(self._events)
