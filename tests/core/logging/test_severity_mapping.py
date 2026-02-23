from io import StringIO
import json

from core.logging_utils.structured_logger import StructuredLogger
from core.telemetry.types import TelemetrySeverity


def test_severity_is_preserved():
    buf = StringIO()
    logger = StructuredLogger("run-002", buf, None)

    logger.log(TelemetrySeverity.CRITICAL, "boom")

    record = json.loads(buf.getvalue())
    assert record["severity"] == "critical"
