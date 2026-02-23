import pytest
from copy import deepcopy

from dashboard.snapshot_loader import load_dashboard_snapshot


# ─────────────────────────────────────────────
# Helpers (test-only)
# ─────────────────────────────────────────────

def _load_interpretation():
    _, snapshot = load_dashboard_snapshot()
    assert snapshot is not None
    assert hasattr(snapshot, "interpretation")
    return snapshot.interpretation


def _with_panel_override(interpretation, **overrides):
    """
    Return a modified interpretation copy with panel label overrides.
    This simulates contradictions without mutating original snapshot.
    """
    clone = deepcopy(interpretation)

    for panel_name, label in overrides.items():
        assert panel_name in clone
        panel = clone[panel_name]
        assert isinstance(panel, dict)
        panel["label"] = label

    return clone


def _with_many_contradictions():
    """
    Maximal contradiction scenario.
    """
    return _with_panel_override(
        _load_interpretation(),
        market_regime="RISK_OFF",
        risk_climate="LOW",
        strategy_stress="HIGH",
        capital_pressure="LOW",
    )


# ─────────────────────────────────────────────
# Phase-7.3 — Trust Surface Contracts
# ─────────────────────────────────────────────

def test_trust_section_is_present():
    """
    Phase-7.3 must expose a trust surface.
    """
    interpretation = _load_interpretation()
    assert "trust" in interpretation


def test_trust_is_deterministic_for_same_interpretation():
    """
    Same interpretation → identical trust output.
    """
    i1 = _load_interpretation()
    i2 = _load_interpretation()

    assert i1["trust"] == i2["trust"]


def test_trust_is_stable_when_no_contradictions():
    """
    Default snapshot must be fully trusted.
    """
    trust = _load_interpretation()["trust"]

    assert trust["status"] == "STABLE"
    assert trust["penalty_applied"] == 0.0
    assert trust["base_confidence"] == trust["degraded_confidence"]


def test_single_contradiction_reduces_confidence():
    """
    One contradiction must degrade confidence.
    """
    modified = _with_panel_override(
        _load_interpretation(),
        market_regime="RISK_OFF",
        risk_climate="LOW",
    )

    trust = modified["trust"]

    assert trust["status"] == "DEGRADED"
    assert trust["penalty_applied"] > 0.0
    assert trust["degraded_confidence"] < trust["base_confidence"]


def test_multiple_contradictions_compound_penalty():
    """
    Multiple contradictions must compound penalty.
    """
    trust = _with_many_contradictions()["trust"]

    assert trust["penalty_applied"] > 0.2
    assert trust["degraded_confidence"] < trust["base_confidence"]


def test_confidence_never_goes_negative():
    """
    Confidence must have a hard floor at 0.0.
    """
    trust = _with_many_contradictions()["trust"]

    assert trust["degraded_confidence"] >= 0.0


def test_trust_becomes_untrustworthy_below_threshold():
    """
    Below threshold → UNTRUSTWORTHY.
    """
    trust = _with_many_contradictions()["trust"]

    assert trust["status"] == "UNTRUSTWORTHY"


def test_trust_contains_human_explanation():
    """
    Trust surface must explain itself.
    """
    trust = _load_interpretation()["trust"]

    assert isinstance(trust["explanation"], str)
    assert len(trust["explanation"]) > 20


def test_trust_lists_contributing_contradictions():
    """
    Trust must list contradiction IDs or descriptions.
    """
    trust = _with_many_contradictions()["trust"]

    assert isinstance(trust["contributors"], list)
    assert len(trust["contributors"]) >= 1


def test_trust_does_not_mutate_interpretation():
    """
    Trust evaluation must not mutate interpretation panels.
    """
    interpretation = _load_interpretation()
    before = deepcopy(interpretation)

    _ = interpretation["trust"]

    assert interpretation == before


def test_trust_has_no_execution_or_governance_authority():
    """
    Trust surface must never contain action semantics.
    """
    trust = _load_interpretation()["trust"]

    forbidden = {
        "execute",
        "block",
        "approve",
        "reject",
        "arm",
        "disarm",
        "capital",
        "intent",
    }

    assert forbidden.isdisjoint(trust.keys())


def test_trust_has_no_wallclock_dependency():
    """
    Trust must be snapshot-anchored, not time-dependent.
    """
    t1 = _load_interpretation()["trust"]
    t2 = _load_interpretation()["trust"]

    assert t1 == t2
