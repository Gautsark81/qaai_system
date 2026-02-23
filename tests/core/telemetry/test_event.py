import pytest
from dataclasses import FrozenInstanceError

from core.telemetry.event import TelemetryEvent
from core.telemetry.types import TelemetryCategory, TelemetrySeverity


def test_event_creation_success():
    event = TelemetryEvent.create(
        category=TelemetryCategory.MARKET_DATA,
        severity=TelemetrySeverity.INFO,
        run_id="run-123",
        payload={"price": 100},
        strategy_id="strat-A",
        order_id="ord-1",
    )

    assert event.event_id is not None
    assert event.run_id == "run-123"
    assert event.strategy_id == "strat-A"
    assert event.order_id == "ord-1"
    assert event.payload == {"price": 100}
    assert event.timestamp is not None


def test_event_requires_run_id():
    with pytest.raises(ValueError):
        TelemetryEvent.create(
            category=TelemetryCategory.ERROR,
            severity=TelemetrySeverity.CRITICAL,
            run_id="",
            payload={"msg": "fail"},
        )


def test_event_is_immutable():
    event = TelemetryEvent.create(
        category=TelemetryCategory.ERROR,
        severity=TelemetrySeverity.ERROR,
        run_id="run-imm",
        payload={"x": 1},
    )

    with pytest.raises(FrozenInstanceError):
        event.run_id = "new-run"


def test_payload_is_defensively_copied():
    payload = {"a": 1}
    event = TelemetryEvent.create(
        category=TelemetryCategory.STRATEGY_SIGNAL,
        severity=TelemetrySeverity.INFO,
        run_id="run-copy",
        payload=payload,
    )

    payload["a"] = 999
    assert event.payload["a"] == 1
