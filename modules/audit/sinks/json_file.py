# modules/audit/sinks/json_file.py

import json
from pathlib import Path

from modules.audit.sink import AuditSink
from modules.audit.events import AuditEvent


class JsonFileAuditSink(AuditSink):
    """
    Append-only JSONL audit sink.
    Safe for production use.
    """

    def __init__(self, path: str):
        self._path = Path(path)

    def _emit(self, event: AuditEvent) -> None:
        record = {
            "timestamp": event.timestamp.isoformat(),
            "category": event.category,
            "entity_id": event.entity_id,
            "message": event.message,
        }

        # Append-only, no read-modify-write
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
