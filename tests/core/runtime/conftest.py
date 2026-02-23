import pytest
from datetime import datetime, timezone

from core.telemetry.emitter import TelemetryEmitter
from core.telemetry.sink import TelemetrySink


class InMemorySink(TelemetrySink):
    def __init__(self):
        self.events = []

    def emit(self, event):
        self.events.append(event)


@pytest.fixture
def telemetry_sink():
    return InMemorySink()


@pytest.fixture
def telemetry_emitter(telemetry_sink):
    return TelemetryEmitter([telemetry_sink])


@pytest.fixture
def fixed_time():
    return datetime(2025, 1, 1, tzinfo=timezone.utc)
