# tests/phase_h/test_observability_side_effect_free.py

from modules.audit.sink import AuditSink
from modules.audit.events import AuditEvent
from datetime import datetime


def test_audit_sink_never_raises():
    sink = AuditSink()

    # must not raise
    sink.emit(
        AuditEvent(
            timestamp=datetime.utcnow(),
            category="TEST",
            entity_id="x",
            message="noop",
        )
    )
