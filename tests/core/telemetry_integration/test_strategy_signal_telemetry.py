from core.telemetry.types import TelemetryCategory, TelemetrySeverity
from core.telemetry.event import TelemetryEvent


def test_strategy_emits_signal_once(
    telemetry_emitter,
    telemetry_sink,
    run_id,
):
    # --- simulate strategy decision ---
    event = TelemetryEvent.create(
        category=TelemetryCategory.STRATEGY_SIGNAL,
        severity=TelemetrySeverity.INFO,
        run_id=run_id,
        strategy_id="dummy_strategy",
        payload={
            "direction": "LONG",
            "probability": 0.65,
            "threshold": 0.6,
        },
    )

    telemetry_emitter.emit(event)

    # --- assertions ---
    assert len(telemetry_sink.events) == 1

    emitted = telemetry_sink.events[0]
    assert emitted.category == TelemetryCategory.STRATEGY_SIGNAL
    assert emitted.severity == TelemetrySeverity.INFO
    assert emitted.run_id == run_id
    assert emitted.strategy_id == "dummy_strategy"
