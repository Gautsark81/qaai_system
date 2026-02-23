import pytest

from core.telemetry.emitter import TelemetryEmitter
from core.telemetry.event import TelemetryEvent
from core.telemetry.types import TelemetryCategory, TelemetrySeverity
from core.telemetry.sink import TelemetrySink


class DummySink(TelemetrySink):
    def __init__(self):
        self.events = []

    def emit(self, event):
        self.events.append(event)


def _sample_event():
    return TelemetryEvent.create(
        category=TelemetryCategory.HEARTBEAT,
        severity=TelemetrySeverity.DEBUG,
        run_id="run-emitter",
        payload={"alive": True},
    )


def test_emitter_requires_at_least_one_sink():
    with pytest.raises(ValueError):
        TelemetryEmitter([])


def test_emitter_fans_out_to_all_sinks():
    sink1 = DummySink()
    sink2 = DummySink()
    emitter = TelemetryEmitter([sink1, sink2])

    event = _sample_event()
    emitter.emit(event)

    assert sink1.events == [event]
    assert sink2.events == [event]
