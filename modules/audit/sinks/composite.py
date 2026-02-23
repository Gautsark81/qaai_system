# modules/audit/sinks/composite.py

from typing import Iterable

from modules.audit.sink import AuditSink
from modules.audit.events import AuditEvent


class CompositeAuditSink(AuditSink):
    """
    Fan-out sink.
    Each child sink is isolated.
    """

    def __init__(self, sinks: Iterable[AuditSink]):
        self._sinks = list(sinks)

    def _emit(self, event: AuditEvent) -> None:
        for sink in self._sinks:
            try:
                sink.emit(event)
            except Exception:
                # Absolute isolation between sinks
                continue
