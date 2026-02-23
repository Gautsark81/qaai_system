import json
from pathlib import Path

from core.telemetry.event import TelemetryEvent
from core.telemetry.types import TelemetryCategory, TelemetrySeverity
from core.telemetry.sinks.null import NullSink
from core.telemetry.sinks.jsonl import JsonlSink


def _event():
    return TelemetryEvent.create(
        category=TelemetryCategory.PNL_UPDATE,
        severity=TelemetrySeverity.INFO,
        run_id="run-sink",
        payload={"pnl": 123.45},
    )


def test_null_sink_does_not_fail():
    sink = NullSink()
    sink.emit(_event())  # should do nothing, not crash


def test_jsonl_sink_writes_event(tmp_path: Path):
    file_path = tmp_path / "telemetry.jsonl"
    sink = JsonlSink(file_path)

    event = _event()
    sink.emit(event)

    lines = file_path.read_text().splitlines()
    assert len(lines) == 1

    record = json.loads(lines[0])
    assert record["run_id"] == "run-sink"
    assert record["payload"]["pnl"] == 123.45
