# modules/audit/sinks/console.py

from modules.audit.sink import AuditSink
from modules.audit.events import AuditEvent


class ConsoleAuditSink(AuditSink):
    """
    Human-readable audit output.
    Intended for dev / staging / dry-run.
    """

    def _emit(self, event: AuditEvent) -> None:
        print(
            f"[{event.timestamp.isoformat()}] "
            f"{event.category} "
            f"{event.entity_id} — {event.message}"
        )
