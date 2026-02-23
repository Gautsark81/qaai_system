import pytest

from dashboard.snapshot_loader import load_dashboard_snapshot


def test_snapshot_has_lineage_fields():
    _, snapshot = load_dashboard_snapshot()

    assert hasattr(snapshot, "parent_hash")
    assert hasattr(snapshot, "lineage_depth")
    assert hasattr(snapshot, "cause")


def test_genesis_snapshot_lineage_defaults():
    _, snapshot = load_dashboard_snapshot()

    assert snapshot.parent_hash is None
    assert snapshot.lineage_depth == 0
    assert snapshot.cause == "BOOT"


def test_snapshot_lineage_is_immutable():
    _, snapshot = load_dashboard_snapshot()

    with pytest.raises(TypeError):
        snapshot.parent_hash = "tamper"

    with pytest.raises(TypeError):
        snapshot.lineage_depth = 99

    with pytest.raises(TypeError):
        snapshot.cause = "HACKED"


def test_snapshot_hash_independent_of_timestamp_but_respects_lineage():
    _, s1 = load_dashboard_snapshot()
    _, s2 = load_dashboard_snapshot()

    # Same genesis snapshot → same hash
    assert s1.hash == s2.hash
    assert s1.lineage_depth == s2.lineage_depth
    assert s1.parent_hash == s2.parent_hash
    assert s1.cause == s2.cause
