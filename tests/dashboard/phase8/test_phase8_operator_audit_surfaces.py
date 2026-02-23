import pytest
from copy import deepcopy
from dataclasses import FrozenInstanceError

from dashboard.domain.dashboard_snapshot import DashboardSnapshot
from tests.dashboard.phase8.test_phase8_operator_read_only_contracts import _load_snapshot


# ─────────────────────────────────────────────
# Phase-8.2 — Operator Audit Surfaces
# ─────────────────────────────────────────────

def test_operator_audit_surface_is_present():
    snapshot = _load_snapshot()
    assert isinstance(snapshot, DashboardSnapshot)
    assert hasattr(snapshot, "operator_audit")


def test_operator_audit_surface_is_read_only():
    snapshot = _load_snapshot()
    audit = snapshot.operator_audit

    with pytest.raises(FrozenInstanceError):
        audit["tamper"] = True


def test_operator_audit_is_snapshot_anchored():
    snapshot = _load_snapshot()
    audit = snapshot.operator_audit

    assert audit["snapshot_hash"] == snapshot.hash
    assert audit["hash_algo"] == snapshot.hash_algo
    assert audit["lineage_depth"] == snapshot.lineage_depth
    assert audit["cause"] == snapshot.cause


def test_operator_audit_is_deterministic():
    s1 = _load_snapshot()
    s2 = _load_snapshot()

    assert s1.operator_audit == s2.operator_audit


def test_operator_audit_does_not_mutate_snapshot():
    snapshot = _load_snapshot()
    before = deepcopy(snapshot)

    _ = snapshot.operator_audit

    assert snapshot == before


def test_operator_audit_contains_only_observational_keys():
    snapshot = _load_snapshot()
    audit = snapshot.operator_audit

    forbidden = {
        "approve",
        "reject",
        "execute",
        "arm",
        "disarm",
        "promote",
        "evaluate_governance",
        "record_governance_decision",
    }

    assert forbidden.isdisjoint(audit.keys())


def test_operator_audit_contains_operator_view_checksum():
    snapshot = _load_snapshot()
    audit = snapshot.operator_audit

    assert "operator_view_hash" in audit
    assert isinstance(audit["operator_view_hash"], str)
    assert len(audit["operator_view_hash"]) > 0


def test_operator_audit_is_non_binding():
    snapshot = _load_snapshot()
    audit = snapshot.operator_audit

    assert audit["is_advisory"] is True
    assert audit["can_trigger_actions"] is False


def test_operator_audit_has_no_wallclock_dependency():
    snapshot = _load_snapshot()

    a1 = snapshot.operator_audit
    a2 = snapshot.operator_audit

    assert a1 == a2
