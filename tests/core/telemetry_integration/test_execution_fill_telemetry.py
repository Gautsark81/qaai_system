from core.telemetry.types import TelemetryCategory, TelemetrySeverity
from core.telemetry.event import TelemetryEvent


def test_execution_fill_emits_once(
    telemetry_emitter,
    telemetry_sink,
    run_id,
):
    event = TelemetryEvent.create(
        category=TelemetryCategory.EXECUTION_FILL,
        severity=TelemetrySeverity.INFO,
        run_id=run_id,
        order_id="order-123",
        payload={
            "filled_qty": 10,
            "avg_price": 2510.5,
            "latency_ms": 42,
        },
    )

    telemetry_emitter.emit(event)

    assert len(telemetry_sink.events) == 1
    assert telemetry_sink.events[0].category == TelemetryCategory.EXECUTION_FILL
