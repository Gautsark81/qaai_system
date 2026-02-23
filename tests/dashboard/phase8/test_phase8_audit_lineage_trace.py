import pytest
from copy import deepcopy
from datetime import datetime, timezone

from dashboard.domain.dashboard_snapshot import DashboardSnapshot


def _make_snapshot():
    """
    Canonical minimal snapshot for Phase-8 tests.
    No fixtures. No services. Deterministic.
    """
    core = {
        "system": {"state": "OK"},
        "market": {"regime": "UNKNOWN"},
        "strategies": {},
        "capital": {"allocated": 0.0},
        "execution": {"armed": False},
        "governance": {"status": "UNCHECKED"},
        "meta": {"source": "phase8_test"},
        "timestamp": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }

    class _Mood:
        mood = 0.5

    return DashboardSnapshot(
        core=core,
        system_mood_detail=_Mood(),
        system_mood_drift=None,
        violation_pulse=None,
    )


def test_audit_lineage_surface_is_present():
    snapshot = _make_snapshot()
    assert hasattr(snapshot, "audit_lineage")


def test_audit_lineage_is_read_only():
    snapshot = _make_snapshot()
    lineage = snapshot.audit_lineage

    with pytest.raises(Exception):
        lineage["tamper"] = True


def test_audit_lineage_is_snapshot_anchored():
    snapshot = _make_snapshot()
    lineage = snapshot.audit_lineage

    assert lineage["snapshot_hash"] == snapshot.hash
    assert lineage["lineage_depth"] == snapshot.lineage_depth
    assert lineage["cause"] == snapshot.cause


def test_audit_lineage_contains_operator_and_audit_hashes():
    snapshot = _make_snapshot()
    lineage = snapshot.audit_lineage

    assert "operator_view_hash" in lineage
    assert "operator_audit_hash" in lineage


def test_audit_lineage_is_deterministic():
    s1 = _make_snapshot()
    s2 = _make_snapshot()

    assert s1.audit_lineage == s2.audit_lineage


def test_audit_lineage_does_not_mutate_snapshot():
    snapshot = _make_snapshot()
    before = deepcopy(snapshot)

    _ = snapshot.audit_lineage

    assert snapshot.hash == before.hash
    assert snapshot.lineage_depth == before.lineage_depth


def test_audit_lineage_tracks_promotion_chain():
    parent = _make_snapshot()
    child = parent.promote(cause="PHASE8_PROMOTION_TEST")

    lineage = child.audit_lineage

    assert lineage["parent_hash"] == parent.hash
    assert lineage["lineage_depth"] == parent.lineage_depth + 1
    assert lineage["cause"] == "PHASE8_PROMOTION_TEST"


def test_audit_lineage_is_non_binding():
    snapshot = _make_snapshot()
    lineage = snapshot.audit_lineage

    assert lineage["is_advisory"] is True
    assert lineage["can_trigger_actions"] is False


def test_audit_lineage_has_no_wallclock_dependency():
    snapshot = _make_snapshot()

    l1 = snapshot.audit_lineage
    l2 = snapshot.audit_lineage

    assert l1 == l2
