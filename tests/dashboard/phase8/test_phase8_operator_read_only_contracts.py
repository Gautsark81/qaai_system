# tests/dashboard/phase8/test_phase8_operator_read_only_contracts.py

from copy import deepcopy
from datetime import datetime, timezone

import pytest

from dashboard.snapshot_loader import load_dashboard_snapshot


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _load_snapshot():
    state, snapshot = load_dashboard_snapshot()
    assert snapshot is not None
    return snapshot


# ─────────────────────────────────────────────
# Core Presence
# ─────────────────────────────────────────────

def test_operator_surface_is_present():
    """
    Phase-8.1 must expose an operator surface.
    """
    snapshot = _load_snapshot()

    assert hasattr(snapshot, "operator")
    operator = snapshot.operator

    assert isinstance(operator, dict)


def test_operator_surface_is_read_only():
    """
    Operator surface must be immutable.
    """
    snapshot = _load_snapshot()
    operator = snapshot.operator

    with pytest.raises(Exception):
        operator["new_key"] = "ILLEGAL"

    with pytest.raises(Exception):
        operator.clear()


# ─────────────────────────────────────────────
# Allowed Operator Data
# ─────────────────────────────────────────────

def test_operator_exposes_only_observational_sections():
    """
    Operator may observe but never command.
    """
    snapshot = _load_snapshot()
    operator = snapshot.operator

    allowed = {
        "system",
        "market",
        "strategies",
        "capital",
        "execution",
        "governance",
        "interpretation",
        "meta",
    }

    assert set(operator.keys()).issubset(allowed)


def test_operator_exposes_interpretation_read_only():
    """
    Interpretation surfaced to operator must be read-only.
    """
    snapshot = _load_snapshot()
    operator = snapshot.operator

    interp = operator.get("interpretation")
    assert interp is not None

    before = deepcopy(interp)

    _ = interp.get("consistency")
    _ = interp.get("trust")
    _ = interp.get("stability")

    assert interp == before


# ─────────────────────────────────────────────
# Forbidden Authority
# ─────────────────────────────────────────────

def test_operator_has_no_execution_authority():
    """
    Operator must not expose execution hooks.
    """
    snapshot = _load_snapshot()
    operator = snapshot.operator

    forbidden = {
        "place_order",
        "cancel_order",
        "modify_order",
        "execute",
    }

    assert forbidden.isdisjoint(operator.keys())


def test_operator_has_no_capital_authority():
    """
    Operator must not expose capital mutation.
    """
    snapshot = _load_snapshot()
    operator = snapshot.operator

    forbidden = {
        "allocate_capital",
        "reduce_capital",
        "throttle",
    }

    assert forbidden.isdisjoint(operator.keys())


def test_operator_has_no_governance_authority():
    """
    Operator must not approve or reject decisions.
    """
    snapshot = _load_snapshot()
    operator = snapshot.operator

    forbidden = {
        "approve",
        "reject",
        "vote",
        "override",
    }

    assert forbidden.isdisjoint(operator.keys())


# ─────────────────────────────────────────────
# Determinism & Safety
# ─────────────────────────────────────────────

def test_operator_surface_is_deterministic():
    """
    Same snapshot → identical operator view.
    """
    s1 = _load_snapshot()
    s2 = _load_snapshot()

    assert s1.hash == s2.hash
    assert s1.operator == s2.operator


def test_operator_surface_does_not_mutate_snapshot():
    """
    Reading operator data must not mutate snapshot.
    """
    snapshot = _load_snapshot()
    before = deepcopy(snapshot)

    _ = snapshot.operator

    assert snapshot == before


def test_operator_surface_has_no_wallclock_dependency():
    """
    Operator view must be snapshot-anchored.
    """
    snapshot = _load_snapshot()

    o1 = snapshot.operator
    _ = datetime.now(timezone.utc)
    o2 = snapshot.operator

    assert o1 == o2
