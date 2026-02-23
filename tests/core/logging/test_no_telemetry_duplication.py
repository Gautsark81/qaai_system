from io import StringIO
import json

from core.logging_utils.structured_logger import StructuredLogger
from core.telemetry.event import TelemetryEvent
from core.telemetry.types import TelemetryCategory, TelemetrySeverity


def test_logger_does_not_emit_telemetry():
    buf = StringIO()
    logger = StructuredLogger("run-003", buf, None)

    event = TelemetryEvent.create(
        category=TelemetryCategory.ERROR,
        severity=TelemetrySeverity.ERROR,
        run_id="run-003",
        payload={"msg": "fail"},
    )

    logger.from_event(event)

    record = json.loads(buf.getvalue())
    assert record["category"] == "error"
    assert "event_id" in record
