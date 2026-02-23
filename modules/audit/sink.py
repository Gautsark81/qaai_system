# modules/audit/sink.py

from modules.audit.events import AuditEvent


class AuditSink:
    """
    Base audit sink.

    HARD GUARANTEES:
    - emit() must NEVER raise
    - emit() must NEVER block core logic
    - Side-effect failures are swallowed
    """

    def emit(self, event: AuditEvent) -> None:
        try:
            self._emit(event)
        except Exception:
            # Absolute rule: audit must not affect trading
            return

    def _emit(self, event: AuditEvent) -> None:
        # Default no-op
        return
