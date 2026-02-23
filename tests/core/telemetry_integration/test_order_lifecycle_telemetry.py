from core.telemetry.types import TelemetryCategory, TelemetrySeverity
from core.telemetry.event import TelemetryEvent


def test_order_lifecycle_emits_once(
    telemetry_emitter,
    telemetry_sink,
    run_id,
):
    event = TelemetryEvent.create(
        category=TelemetryCategory.ORDER_LIFECYCLE,
        severity=TelemetrySeverity.INFO,
        run_id=run_id,
        strategy_id="dummy_strategy",
        order_id="order-123",
        payload={
            "action": "CREATE",
            "symbol": "RELIANCE",
            "qty": 10,
        },
    )

    telemetry_emitter.emit(event)

    assert len(telemetry_sink.events) == 1
    assert telemetry_sink.events[0].order_id == "order-123"
