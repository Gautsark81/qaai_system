import pytest
from datetime import datetime, timedelta, timezone

from dashboard.snapshot_loader import load_dashboard_snapshot


def _fake_decisions(snapshot, records):
    """
    Helper to create multiple governance + operator records
    without mutating snapshot.
    """
    decisions = []
    for r in records:
        decisions.append(
            snapshot.record_governance_decision(
                status=r["status"],
                reason=r["reason"],
                severity=r["severity"],
            )
        )
    return decisions


def _fake_acknowledgements(snapshot, events):
    acks = []
    for e in events:
        acks.append(
            snapshot.record_operator_acknowledgement(
                event_type=e["event_type"],
                context=e["context"],
            )
        )
    return acks


# ─────────────────────────────────────────────
# Phase-2.4 — Surface exposure
# ─────────────────────────────────────────────

def test_snapshot_exposes_decision_drift_surface():
    """
    Phase-2.4 must expose a READ-ONLY analytics surface.
    """
    _, snapshot = load_dashboard_snapshot()

    assert hasattr(snapshot, "decision_drift_metrics"), (
        "Snapshot must expose decision drift analytics surface"
    )


# ─────────────────────────────────────────────
# Drift invariants
# ─────────────────────────────────────────────

def test_decision_drift_metrics_are_read_only():
    """
    Decision drift analytics must be immutable.
    """
    _, snapshot = load_dashboard_snapshot()
    metrics = snapshot.decision_drift_metrics

    with pytest.raises(Exception):
        metrics["alert_fatigue_index"] = 1.0


def test_decision_drift_is_snapshot_derived_only():
    """
    Analytics must be derived only from records bound to snapshot hash.
    """
    _, snapshot = load_dashboard_snapshot()

    metrics = snapshot.decision_drift_metrics

    assert metrics["derived_from"] == snapshot.hash
    assert metrics["timestamp"] <= datetime.now(timezone.utc)


# ─────────────────────────────────────────────
# Core analytics contracts
# ─────────────────────────────────────────────

def test_alert_fatigue_index_present_and_bounded():
    """
    Alert fatigue index must exist and be normalized.
    """
    _, snapshot = load_dashboard_snapshot()
    metrics = snapshot.decision_drift_metrics

    assert "alert_fatigue_index" in metrics
    assert 0.0 <= metrics["alert_fatigue_index"] <= 1.0


def test_repeated_approval_rate_present():
    """
    System must detect repeated approvals under similar conditions.
    """
    _, snapshot = load_dashboard_snapshot()
    metrics = snapshot.decision_drift_metrics

    assert "repeated_approval_rate" in metrics
    assert 0.0 <= metrics["repeated_approval_rate"] <= 1.0


def test_contradiction_rate_present():
    """
    Contradiction rate measures conflicting judgments over time.
    """
    _, snapshot = load_dashboard_snapshot()
    metrics = snapshot.decision_drift_metrics

    assert "contradiction_rate" in metrics
    assert 0.0 <= metrics["contradiction_rate"] <= 1.0


def test_decision_latency_variance_present():
    """
    Decision time variance indicates instability or fatigue.
    """
    _, snapshot = load_dashboard_snapshot()
    metrics = snapshot.decision_drift_metrics

    assert "decision_latency_variance" in metrics
    assert metrics["decision_latency_variance"] >= 0.0


# ─────────────────────────────────────────────
# Non-authority guarantees
# ─────────────────────────────────────────────

def test_decision_drift_metrics_are_non_binding():
    """
    Analytics must never issue commands or authority.
    """
    _, snapshot = load_dashboard_snapshot()
    metrics = snapshot.decision_drift_metrics

    assert metrics["is_advisory"] is True
    assert metrics["can_trigger_actions"] is False


def test_decision_drift_does_not_modify_snapshot():
    """
    Accessing analytics must not mutate snapshot.
    """
    _, snapshot = load_dashboard_snapshot()
    original_hash = snapshot.hash

    _ = snapshot.decision_drift_metrics

    assert snapshot.hash == original_hash
