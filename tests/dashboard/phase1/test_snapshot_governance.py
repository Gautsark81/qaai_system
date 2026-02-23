import pytest
from dataclasses import FrozenInstanceError

from dashboard.snapshot_loader import load_dashboard_snapshot


# ─────────────────────────────────────────────
# Phase-1.7 — Governance Hooks (Tests First)
# ─────────────────────────────────────────────

def test_snapshot_has_governance_fields():
    _, snapshot = load_dashboard_snapshot()

    assert hasattr(snapshot, "governance_status")
    assert hasattr(snapshot, "governance_reason")
    assert hasattr(snapshot, "governance_checked_at")


def test_default_governance_state_is_unchecked():
    _, snapshot = load_dashboard_snapshot()

    assert snapshot.governance_status == "UNCHECKED"
    assert snapshot.governance_reason is None
    assert snapshot.governance_checked_at is None


def test_governance_fields_are_immutable():
    _, snapshot = load_dashboard_snapshot()

    with pytest.raises(FrozenInstanceError):
        snapshot.governance_status = "APPROVED"

    with pytest.raises(FrozenInstanceError):
        snapshot.governance_reason = "manual override"

    with pytest.raises(FrozenInstanceError):
        snapshot.governance_checked_at = "now"


def test_governance_does_not_affect_snapshot_hash():
    _, s1 = load_dashboard_snapshot()
    _, s2 = load_dashboard_snapshot()

    assert s1.hash == s2.hash
    assert s1.governance_status == "UNCHECKED"


def test_promoted_snapshot_inherits_governance_state():
    _, parent = load_dashboard_snapshot()
    child = parent.promote(cause="GOVERNANCE_TEST")

    assert child.governance_status == parent.governance_status
    assert child.governance_reason == parent.governance_reason
    assert child.governance_checked_at == parent.governance_checked_at


def test_governance_is_not_part_of_core_snapshot():
    _, snapshot = load_dashboard_snapshot()

    core_keys = snapshot.core.keys()

    assert "governance_status" not in core_keys
    assert "governance_reason" not in core_keys
    assert "governance_checked_at" not in core_keys
