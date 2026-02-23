import json
from io import StringIO

from core.logging_utils.structured_logger import StructuredLogger
from core.telemetry.types import TelemetrySeverity


def test_log_is_valid_json():
    buffer = StringIO()
    logger = StructuredLogger(
        run_id="run-001",
        stream=buffer,
        jsonl_path=None,
    )

    logger.log(
        severity=TelemetrySeverity.INFO,
        message="test_message",
        extra={"x": 1},
    )

    output = buffer.getvalue().strip()
    record = json.loads(output)

    assert record["run_id"] == "run-001"
    assert record["message"] == "test_message"
    assert record["severity"] == "info"
    assert record["extra"]["x"] == 1
