from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List


@dataclass(frozen=True)
class AuditEvent:
    """
    Immutable audit record for compliance & operator visibility.
    """
    timestamp: datetime
    dna: str
    event_type: str
    payload: Dict[str, Any]


class AuditLogStore:
    """
    Append-only audit log.
    """

    def __init__(self):
        self._events: List[AuditEvent] = []

    def append(self, event: AuditEvent) -> None:
        if not isinstance(event, AuditEvent):
            raise TypeError("AuditLogStore accepts only AuditEvent objects")
        self._events.append(event)

    def all(self) -> List[AuditEvent]:
        return list(self._events)
