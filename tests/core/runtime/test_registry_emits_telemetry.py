from datetime import datetime, timezone

from core.runtime.run_registry import RunRegistry
from core.runtime.run_context import RunContext
from core.telemetry.types import TelemetryCategory


def test_registry_emits_telemetry_on_register(telemetry_emitter, telemetry_sink):
    registry = RunRegistry(telemetry=telemetry_emitter)

    ctx = RunContext(
        run_id="run-telemetry",
        git_commit="abc123",
        phase_version="12",
        config_fingerprint="cfg",
        start_time=datetime.now(timezone.utc),
    )

    registry.register(ctx)

    assert len(telemetry_sink.events) == 1
    assert telemetry_sink.events[0].category == TelemetryCategory.HEARTBEAT
