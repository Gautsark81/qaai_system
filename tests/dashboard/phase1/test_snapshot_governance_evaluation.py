import pytest
from dataclasses import FrozenInstanceError

from dashboard.snapshot_loader import load_dashboard_snapshot


def test_snapshot_has_governance_evaluate_method():
    _, snapshot = load_dashboard_snapshot()
    assert hasattr(snapshot, "evaluate_governance")


def test_governance_evaluation_returns_new_snapshot():
    _, parent = load_dashboard_snapshot()

    evaluated = parent.evaluate_governance(
        status="APPROVED",
        reason="All checks passed",
    )

    assert evaluated is not parent


def test_governance_evaluation_promotes_snapshot():
    _, parent = load_dashboard_snapshot()

    evaluated = parent.evaluate_governance(
        status="APPROVED",
        reason="OK",
    )

    assert evaluated.parent_hash == parent.hash
    assert evaluated.lineage_depth == parent.lineage_depth + 1
    assert evaluated.cause == "GOVERNANCE_EVALUATION"


def test_governance_fields_are_set_on_evaluated_snapshot():
    _, parent = load_dashboard_snapshot()

    evaluated = parent.evaluate_governance(
        status="REJECTED",
        reason="Risk breach",
    )

    assert evaluated.governance_status == "REJECTED"
    assert evaluated.governance_reason == "Risk breach"
    assert evaluated.governance_checked_at is not None


def test_governance_evaluation_does_not_modify_parent():
    _, parent = load_dashboard_snapshot()

    _ = parent.evaluate_governance(
        status="APPROVED",
        reason="OK",
    )

    assert parent.governance_status == "UNCHECKED"
    assert parent.governance_reason is None
    assert parent.governance_checked_at is None


def test_governance_evaluation_does_not_change_core_hash():
    _, parent = load_dashboard_snapshot()

    evaluated = parent.evaluate_governance(
        status="APPROVED",
        reason="OK",
    )

    # core hash contribution must remain unchanged
    assert evaluated.hash != parent.hash
    assert evaluated.parent_hash == parent.hash


def test_governance_evaluation_is_deterministic():
    _, parent = load_dashboard_snapshot()

    g1 = parent.evaluate_governance(
        status="APPROVED",
        reason="OK",
    )

    g2 = parent.evaluate_governance(
        status="APPROVED",
        reason="OK",
    )

    assert g1.hash == g2.hash


def test_evaluated_snapshot_is_immutable():
    _, parent = load_dashboard_snapshot()

    evaluated = parent.evaluate_governance(
        status="APPROVED",
        reason="OK",
    )

    with pytest.raises(FrozenInstanceError):
        evaluated.governance_status = "REJECTED"


def test_invalid_governance_status_is_rejected():
    _, parent = load_dashboard_snapshot()

    with pytest.raises(ValueError):
        parent.evaluate_governance(
            status="INVALID_STATUS",
            reason="Nope",
        )
