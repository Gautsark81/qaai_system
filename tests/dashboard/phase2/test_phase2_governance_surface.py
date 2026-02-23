from datetime import datetime, timezone
import pytest
from dataclasses import FrozenInstanceError

from dashboard.snapshot_loader import load_dashboard_snapshot


# ─────────────────────────────────────────────
# Phase-2.2 — Governance Judgment Surface
# TESTS DEFINE CONTRACT
# ─────────────────────────────────────────────


def test_phase2_snapshot_exposes_governance_surface():
    """
    Phase-2 must expose a governance judgment recorder.
    This surface RECORDS judgment — it does NOT act.
    """
    _, snapshot = load_dashboard_snapshot()

    assert hasattr(snapshot, "record_governance_decision"), \
        "Phase-2 must expose governance judgment surface"


def test_governance_decision_requires_mandatory_fields():
    """
    Governance decisions must require:
    - status
    - reason
    - severity
    """
    _, snapshot = load_dashboard_snapshot()

    with pytest.raises(ValueError):
        snapshot.record_governance_decision(
            status="APPROVE",
            reason="",
            severity="HIGH",
        )

    with pytest.raises(ValueError):
        snapshot.record_governance_decision(
            status="APPROVE",
            reason="Looks fine",
            severity="",
        )


def test_governance_decision_status_is_strictly_limited():
    """
    Only allowed governance statuses are permitted.
    """
    _, snapshot = load_dashboard_snapshot()

    with pytest.raises(ValueError):
        snapshot.record_governance_decision(
            status="EXECUTE",
            reason="Invalid",
            severity="HIGH",
        )


def test_governance_decision_is_record_only_and_non_binding():
    """
    Governance judgment must NEVER bind the system.
    """
    _, snapshot = load_dashboard_snapshot()

    decision = snapshot.record_governance_decision(
        status="HOLD",
        reason="Regime unclear",
        severity="MEDIUM",
    )

    assert decision.is_binding is False
    assert decision.snapshot_hash == snapshot.hash


def test_governance_decision_is_timestamped_and_utc():
    """
    Governance decisions must be timestamped in UTC.
    """
    _, snapshot = load_dashboard_snapshot()

    decision = snapshot.record_governance_decision(
        status="REJECT",
        reason="Risk escalation",
        severity="HIGH",
    )

    assert isinstance(decision.recorded_at, datetime)
    assert decision.recorded_at.tzinfo == timezone.utc
    assert decision.recorded_at <= datetime.now(timezone.utc)


def test_governance_decision_is_immutable():
    """
    Governance records are legal artifacts.
    They must be immutable.
    """
    _, snapshot = load_dashboard_snapshot()

    decision = snapshot.record_governance_decision(
        status="APPROVE",
        reason="Conditions acceptable",
        severity="LOW",
    )

    with pytest.raises(FrozenInstanceError):
        decision.status = "REJECT"

    with pytest.raises(FrozenInstanceError):
        decision.reason = "Changed my mind"


def test_governance_decision_does_not_mutate_snapshot():
    """
    Recording a governance decision must NOT:
    - Promote snapshot
    - Change lineage
    - Alter hash
    """
    _, snapshot = load_dashboard_snapshot()

    original_hash = snapshot.hash
    original_depth = snapshot.lineage_depth

    _ = snapshot.record_governance_decision(
        status="HOLD",
        reason="Observation only",
        severity="MEDIUM",
    )

    assert snapshot.hash == original_hash
    assert snapshot.lineage_depth == original_depth


def test_governance_decision_has_no_execution_side_effects():
    """
    Phase-2 governance must not:
    - Arm execution
    - Trigger promotion
    - Enable control
    """
    _, snapshot = load_dashboard_snapshot()

    decision = snapshot.record_governance_decision(
        status="APPROVE",
        reason="Approved for observation",
        severity="LOW",
    )

    assert hasattr(snapshot, "execution_armed")
    assert snapshot.execution_armed is False
    assert decision.is_binding is False
