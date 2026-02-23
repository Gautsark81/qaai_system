import pytest
from copy import deepcopy

from dashboard.domain.dashboard_snapshot import DashboardSnapshot


def _make_snapshot():
    """
    Minimal deterministic snapshot constructor.
    Avoids test coupling to loaders or services.
    """
    return DashboardSnapshot(
        core={
            "system": {"state": "OK"},
            "market": {"regime": "UNKNOWN"},
            "strategies": {},
            "capital": {},
            "execution": {},
            "governance": {},
            "meta": {},
        },
        system_mood_detail=type("Mood", (), {"mood": 0.5})(),
        system_mood_drift=None,
        violation_pulse=None,
    )


# ─────────────────────────────────────────────
# Phase-8.4 — Forensic Replay Surface
# ─────────────────────────────────────────────

def test_forensic_replay_surface_is_present():
    """
    Phase-8.4 must expose a forensic replay surface.
    """
    snapshot = _make_snapshot()
    assert hasattr(snapshot, "forensic_replay")


def test_forensic_replay_is_read_only():
    """
    Forensic replay surface must be immutable.
    """
    snapshot = _make_snapshot()
    replay = snapshot.forensic_replay

    with pytest.raises(Exception):
        replay["tamper"] = True


def test_forensic_replay_is_snapshot_anchored():
    """
    Replay must be explicitly bound to snapshot identity.
    """
    snapshot = _make_snapshot()
    replay = snapshot.forensic_replay

    assert replay["snapshot_hash"] == snapshot.hash
    assert replay["lineage_depth"] == snapshot.lineage_depth
    assert replay["cause"] == snapshot.cause


def test_forensic_replay_contains_operator_view():
    """
    Replay must reconstruct operator-visible view.
    """
    snapshot = _make_snapshot()
    replay = snapshot.forensic_replay

    assert "operator_view" in replay
    assert replay["operator_view"] == snapshot.operator


def test_forensic_replay_contains_operator_audit():
    """
    Replay must include operator audit surface.
    """
    snapshot = _make_snapshot()
    replay = snapshot.forensic_replay

    assert "operator_audit" in replay
    assert replay["operator_audit"] == snapshot.operator_audit


def test_forensic_replay_contains_audit_lineage():
    """
    Replay must include full audit lineage.
    """
    snapshot = _make_snapshot()
    replay = snapshot.forensic_replay

    assert "audit_lineage" in replay
    assert replay["audit_lineage"] == snapshot.audit_lineage


def test_forensic_replay_is_deterministic():
    """
    Same snapshot → identical forensic replay.
    """
    s1 = _make_snapshot()
    s2 = _make_snapshot()

    assert s1.forensic_replay == s2.forensic_replay


def test_forensic_replay_does_not_mutate_snapshot():
    """
    Accessing forensic replay must not mutate snapshot.
    """
    snapshot = _make_snapshot()
    before = deepcopy(snapshot)

    _ = snapshot.forensic_replay

    assert snapshot.hash == before.hash
    assert snapshot.lineage_depth == before.lineage_depth


def test_forensic_replay_is_non_binding():
    """
    Forensic replay must never carry authority.
    """
    snapshot = _make_snapshot()
    replay = snapshot.forensic_replay

    assert replay["is_advisory"] is True
    assert replay["can_trigger_actions"] is False


def test_forensic_replay_has_no_wallclock_dependency():
    """
    Replay must be fully snapshot-derived.
    """
    snapshot = _make_snapshot()

    r1 = snapshot.forensic_replay
    r2 = snapshot.forensic_replay

    assert r1 == r2
