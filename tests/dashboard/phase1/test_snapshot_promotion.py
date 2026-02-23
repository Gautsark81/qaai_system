import pytest

from dashboard.snapshot_loader import load_dashboard_snapshot
from dashboard.domain.dashboard_snapshot import DashboardSnapshot


def test_snapshot_has_promote_method():
    _, snapshot = load_dashboard_snapshot()
    assert hasattr(snapshot, "promote")
    assert callable(snapshot.promote)


def test_promoted_snapshot_has_lineage():
    _, parent = load_dashboard_snapshot()

    child = parent.promote(cause="TEST_PROMOTION")

    assert isinstance(child, DashboardSnapshot)
    assert child.parent_hash == parent.hash
    assert child.lineage_depth == parent.lineage_depth + 1
    assert child.cause == "TEST_PROMOTION"


def test_promotion_preserves_core_snapshot():
    _, parent = load_dashboard_snapshot()
    child = parent.promote(cause="NO_OP")

    assert dict(child.core) == dict(parent.core)


def test_promotion_hash_is_chained():
    _, parent = load_dashboard_snapshot()
    child = parent.promote(cause="CHAIN_TEST")

    assert child.hash != parent.hash


def test_promotion_is_deterministic():
    _, parent = load_dashboard_snapshot()

    c1 = parent.promote(cause="DETERMINISTIC")
    c2 = parent.promote(cause="DETERMINISTIC")

    assert c1.hash == c2.hash
    assert c1.parent_hash == c2.parent_hash
    assert c1.lineage_depth == c2.lineage_depth


def test_promotion_respects_cause():
    _, parent = load_dashboard_snapshot()

    c1 = parent.promote(cause="CAUSE_A")
    c2 = parent.promote(cause="CAUSE_B")

    assert c1.hash != c2.hash
    assert c1.cause == "CAUSE_A"
    assert c2.cause == "CAUSE_B"


def test_promoted_snapshot_is_immutable():
    _, parent = load_dashboard_snapshot()
    child = parent.promote(cause="IMMUTABLE")

    with pytest.raises(TypeError):
        child.parent_hash = "tamper"

    with pytest.raises(TypeError):
        child.lineage_depth = 999

    with pytest.raises(TypeError):
        child.cause = "tamper"


def test_parent_snapshot_remains_unchanged():
    _, parent = load_dashboard_snapshot()
    original_hash = parent.hash

    _ = parent.promote(cause="NO_SIDE_EFFECT")

    assert parent.hash == original_hash
    assert parent.parent_hash is None
    assert parent.lineage_depth == 0
