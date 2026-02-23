import pytest
from dataclasses import FrozenInstanceError

from dashboard.snapshot_loader import load_dashboard_snapshot


# ─────────────────────────────────────────────
# Phase-1.9 — Execution Arming Gate (Tests First)
# ─────────────────────────────────────────────


def test_snapshot_has_execution_arming_fields():
    _, snapshot = load_dashboard_snapshot()

    assert hasattr(snapshot, "execution_armed")
    assert hasattr(snapshot, "execution_arming_reason")
    assert hasattr(snapshot, "execution_arming_checked_at")


def test_default_execution_is_not_armed():
    _, snapshot = load_dashboard_snapshot()

    assert snapshot.execution_armed is False
    assert snapshot.execution_arming_reason is None
    assert snapshot.execution_arming_checked_at is None


def test_execution_arming_fields_are_immutable():
    _, snapshot = load_dashboard_snapshot()

    with pytest.raises(FrozenInstanceError):
        snapshot.execution_armed = True

    with pytest.raises(FrozenInstanceError):
        snapshot.execution_arming_reason = "manual override"


def test_snapshot_has_arm_execution_method():
    _, snapshot = load_dashboard_snapshot()

    assert hasattr(snapshot, "arm_execution")


def test_arm_execution_returns_new_snapshot():
    _, parent = load_dashboard_snapshot()

    armed = parent.arm_execution(
        approved=True,
        reason="Operator approved arming",
    )

    assert armed is not parent


def test_arm_execution_sets_fields():
    _, parent = load_dashboard_snapshot()

    armed = parent.arm_execution(
        approved=True,
        reason="All governance checks passed",
    )

    assert armed.execution_armed is True
    assert armed.execution_arming_reason == "All governance checks passed"
    assert armed.execution_arming_checked_at is not None


def test_arm_execution_does_not_modify_parent():
    _, parent = load_dashboard_snapshot()

    _ = parent.arm_execution(
        approved=True,
        reason="NO SIDE EFFECT",
    )

    assert parent.execution_armed is False
    assert parent.execution_arming_reason is None


def test_arm_execution_promotes_snapshot():
    _, parent = load_dashboard_snapshot()

    armed = parent.arm_execution(
        approved=True,
        reason="PROMOTION TEST",
    )

    assert armed.parent_hash == parent.hash
    assert armed.lineage_depth == parent.lineage_depth + 1


def test_arm_execution_does_not_change_core_hash():
    _, parent = load_dashboard_snapshot()

    armed = parent.arm_execution(
        approved=True,
        reason="CORE IMMUTABLE",
    )

    # Core semantic hash must remain identical
    assert armed.hash != parent.hash  # chained hash differs
    assert armed.core == parent.core


def test_arm_execution_is_deterministic():
    _, parent = load_dashboard_snapshot()

    a1 = parent.arm_execution(
        approved=True,
        reason="DETERMINISTIC",
    )
    a2 = parent.arm_execution(
        approved=True,
        reason="DETERMINISTIC",
    )

    assert a1.hash == a2.hash


def test_invalid_arm_execution_without_reason_is_rejected():
    _, parent = load_dashboard_snapshot()

    with pytest.raises(ValueError):
        parent.arm_execution(
            approved=True,
            reason="",
        )


def test_disarming_execution_is_allowed_and_recorded():
    _, parent = load_dashboard_snapshot()

    disarmed = parent.arm_execution(
        approved=False,
        reason="Risk conditions changed",
    )

    assert disarmed.execution_armed is False
    assert disarmed.execution_arming_reason == "Risk conditions changed"
