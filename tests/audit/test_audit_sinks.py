# tests/audit/test_audit_sinks.py

from datetime import datetime
import tempfile
import os

from modules.audit.events import AuditEvent
from modules.audit.sinks.console import ConsoleAuditSink
from modules.audit.sinks.json_file import JsonFileAuditSink
from modules.audit.sinks.composite import CompositeAuditSink


def make_event():
    return AuditEvent(
        timestamp=datetime.utcnow(),
        category="TEST",
        entity_id="x",
        message="hello",
    )


def test_console_sink_never_raises():
    sink = ConsoleAuditSink()
    sink.emit(make_event())


def test_json_file_sink_writes():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "audit.jsonl")
        sink = JsonFileAuditSink(path)

        sink.emit(make_event())

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        assert len(lines) == 1


def test_composite_sink_isolation():
    class BadSink:
        def emit(self, event):
            raise RuntimeError("boom")

    good = ConsoleAuditSink()
    bad = BadSink()

    sink = CompositeAuditSink([bad, good])
    sink.emit(make_event())  # must not raise
