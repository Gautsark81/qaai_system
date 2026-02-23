import pytest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

from dashboard.snapshot_loader import load_dashboard_snapshot


# ─────────────────────────────────────────────
# Phase-2.3 — Operator Acknowledgement Ledger
# ─────────────────────────────────────────────


def test_snapshot_exposes_operator_acknowledgement_api():
    """
    Phase-2.3 must expose a record-only operator acknowledgement API.
    """
    _, snapshot = load_dashboard_snapshot()

    assert hasattr(snapshot, "record_operator_acknowledgement"), (
        "Snapshot must expose operator acknowledgement recording surface"
    )


def test_operator_acknowledgement_requires_mandatory_fields():
    """
    Operator acknowledgements must require:
    - event_type
    - context
    """
    _, snapshot = load_dashboard_snapshot()

    with pytest.raises(ValueError):
        snapshot.record_operator_acknowledgement(
            event_type="ALERT_ACK",
            context="",
        )

    with pytest.raises(ValueError):
        snapshot.record_operator_acknowledgement(
            event_type="",
            context="Alert reviewed",
        )


def test_operator_acknowledgement_is_snapshot_bound():
    """
    Acknowledgements must be permanently bound to a snapshot hash.
    """
    _, snapshot = load_dashboard_snapshot()

    ack = snapshot.record_operator_acknowledgement(
        event_type="ALERT_ACK",
        context="Reviewed volatility spike",
    )

    assert ack.snapshot_hash == snapshot.hash


def test_operator_acknowledgement_is_time_stamped():
    """
    Operator acknowledgements must be time-stamped at record time.
    """
    _, snapshot = load_dashboard_snapshot()

    ack = snapshot.record_operator_acknowledgement(
        event_type="REVIEW_CONFIRMED",
        context="Reviewed system interpretation",
    )

    assert isinstance(ack.recorded_at, datetime)
    assert ack.recorded_at <= datetime.now(timezone.utc)


def test_operator_acknowledgement_is_immutable():
    """
    Operator acknowledgements must be immutable records.
    """
    _, snapshot = load_dashboard_snapshot()

    ack = snapshot.record_operator_acknowledgement(
        event_type="DEFERRED_DECISION",
        context="Waiting for clearer regime",
    )

    with pytest.raises(FrozenInstanceError):
        ack.context = "Changed later"


def test_operator_acknowledgement_is_non_binding():
    """
    Operator acknowledgements must never be binding.
    """
    _, snapshot = load_dashboard_snapshot()

    ack = snapshot.record_operator_acknowledgement(
        event_type="ESCALATION_MISSED",
        context="No response within SLA window",
    )

    assert ack.is_binding is False


def test_operator_acknowledgement_does_not_modify_snapshot():
    """
    Recording an acknowledgement must not mutate the snapshot.
    """
    _, snapshot = load_dashboard_snapshot()

    original_hash = snapshot.hash

    _ = snapshot.record_operator_acknowledgement(
        event_type="ALERT_ACK",
        context="Acknowledged alert",
    )

    assert snapshot.hash == original_hash


def test_operator_acknowledgement_event_types_are_controlled():
    """
    Event types must be controlled and finite.
    """
    _, snapshot = load_dashboard_snapshot()

    with pytest.raises(ValueError):
        snapshot.record_operator_acknowledgement(
            event_type="RANDOM_EVENT",
            context="Invalid event",
        )
