# tests/strategy_factory/capital/test_throttle_audit_events.py

import pytest

from core.strategy_factory.capital.events import ThrottleAuditEvent


def test_event_creation_basic():
    event = ThrottleAuditEvent.create(
        strategy_id="mean_reversion_v1",
        symbol="RELIANCE",
        requested_capital=100000.0,
        approved_capital=50000.0,
        throttle_type="GLOBAL_LIMIT",
        throttle_reason="Global capital cap reached",
        capital_state_snapshot={"total_allocated": 950000},
        regime_snapshot={"volatility": "high"},
    )

    assert event.requested_capital == 100000.0
    assert event.approved_capital == 50000.0
    assert event.throttle_ratio == 0.5
    assert event.version == "1.0"
    assert event.event_id is not None


def test_event_immutable():
    event = ThrottleAuditEvent.create(
        strategy_id="test",
        symbol="TCS",
        requested_capital=1000,
        approved_capital=1000,
        throttle_type="NONE",
        throttle_reason="No throttle",
        capital_state_snapshot={},
    )

    with pytest.raises(Exception):
        event.approved_capital = 0


def test_serialization_roundtrip():
    event = ThrottleAuditEvent.create(
        strategy_id="alpha",
        symbol="INFY",
        requested_capital=1000,
        approved_capital=700,
        throttle_type="SYMBOL_LIMIT",
        throttle_reason="Symbol cap hit",
        capital_state_snapshot={"symbol_alloc": 200000},
    )

    d = event.to_dict()
    reconstructed = ThrottleAuditEvent.from_dict(d)

    assert reconstructed == event


def test_invalid_requested_capital():
    with pytest.raises(ValueError):
        ThrottleAuditEvent.create(
            strategy_id="alpha",
            symbol="INFY",
            requested_capital=0,
            approved_capital=0,
            throttle_type="INVALID",
            throttle_reason="Invalid",
            capital_state_snapshot={},
        )


def test_invalid_approved_capital():
    with pytest.raises(ValueError):
        ThrottleAuditEvent.create(
            strategy_id="alpha",
            symbol="INFY",
            requested_capital=100,
            approved_capital=-1,
            throttle_type="INVALID",
            throttle_reason="Invalid",
            capital_state_snapshot={},
        )