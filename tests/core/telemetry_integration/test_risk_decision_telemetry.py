from core.telemetry.types import TelemetryCategory, TelemetrySeverity
from core.telemetry.event import TelemetryEvent


def test_risk_manager_emits_decision_once(
    telemetry_emitter,
    telemetry_sink,
    run_id,
):
    event = TelemetryEvent.create(
        category=TelemetryCategory.RISK_DECISION,
        severity=TelemetrySeverity.INFO,
        run_id=run_id,
        strategy_id="dummy_strategy",
        payload={
            "decision": "PASS",
            "rule": "ATR_STOP",
            "reason": "Risk checks passed",
        },
    )

    telemetry_emitter.emit(event)

    assert len(telemetry_sink.events) == 1

    emitted = telemetry_sink.events[0]
    assert emitted.category == TelemetryCategory.RISK_DECISION
    assert emitted.payload["decision"] == "PASS"
