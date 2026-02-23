# modules/bootstrap/audit.py

from modules.audit.sink import AuditSink
from modules.audit.sinks.console import ConsoleAuditSink
from modules.audit.sinks.json_file import JsonFileAuditSink
from modules.audit.sinks.composite import CompositeAuditSink
from modules.runtime.context import get_runtime_flags


def build_audit_sink() -> AuditSink:
    flags = get_runtime_flags()

    if not flags.AUDIT_ENABLED:
        return AuditSink()

    sinks = [ConsoleAuditSink()]

    # Example: file sink can be enabled later
    # sinks.append(JsonFileAuditSink("audit.jsonl"))

    return CompositeAuditSink(sinks)
