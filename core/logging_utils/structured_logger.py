from datetime import datetime, timezone
from typing import Any, Dict, Optional, TextIO
from pathlib import Path

from core.telemetry.types import TelemetrySeverity
from core.telemetry.event import TelemetryEvent

from .formatters import format_record
from .handlers import StreamHandler, JsonlFileHandler


class StructuredLogger:
    def __init__(
        self,
        run_id: str,
        stream: Optional[TextIO],
        jsonl_path: Optional[Path],
    ):
        if not run_id:
            raise ValueError("run_id is mandatory for logging")

        self.run_id = run_id
        self.handlers = []

        if stream:
            self.handlers.append(StreamHandler(stream))

        if jsonl_path:
            self.handlers.append(JsonlFileHandler(jsonl_path))

    def log(
        self,
        severity: TelemetrySeverity,
        message: str,
        *,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id,
            "severity": severity.value,
            "message": message,
            "extra": extra or {},
        }

        line = format_record(record)
        for h in self.handlers:
            h.emit(line)

    def from_event(self, event: TelemetryEvent) -> None:
        record = {
            "timestamp": event.timestamp.isoformat(),
            "run_id": event.run_id,
            "severity": event.severity.value,
            "category": event.category.value,
            "event_id": event.event_id,
            "strategy_id": event.strategy_id,
            "order_id": event.order_id,
            "payload": event.payload,
        }

        line = format_record(record)
        for h in self.handlers:
            h.emit(line)
