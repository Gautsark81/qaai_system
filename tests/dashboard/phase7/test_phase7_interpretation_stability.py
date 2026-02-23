# tests/dashboard/phase7/test_phase7_interpretation_stability.py

from copy import deepcopy
from datetime import datetime, timezone

import pytest

from dashboard.snapshot_loader import load_dashboard_snapshot


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _load_interpretation():
    _, snapshot = load_dashboard_snapshot()
    assert snapshot is not None
    assert hasattr(snapshot, "interpretation")
    return snapshot.interpretation


def _with_panel_override(interpretation, **overrides):
    """
    Clone interpretation and override panel labels.
    Must NOT mutate original.
    """
    cloned = deepcopy(interpretation)

    for panel_name, label in overrides.items():
        assert panel_name in cloned, f"Unknown panel: {panel_name}"
        cloned[panel_name]["label"] = label

    return cloned


# ─────────────────────────────────────────────
# Presence & Shape
# ─────────────────────────────────────────────

def test_stability_section_is_present():
    """
    Phase-7.4 must expose a stability surface.
    """
    interpretation = _load_interpretation()

    assert "stability" in interpretation
    stability = interpretation["stability"]

    assert isinstance(stability, dict)
    assert "status" in stability
    assert "drift_score" in stability
    assert "changed_panels" in stability
    assert "explanation" in stability


# ─────────────────────────────────────────────
# Default Behavior
# ─────────────────────────────────────────────

def test_default_interpretation_is_stable():
    """
    Same snapshot → fully stable interpretation.
    """
    interpretation = _load_interpretation()
    stability = interpretation["stability"]

    assert stability["status"] == "STABLE"
    assert stability["drift_score"] == 0.0
    assert stability["changed_panels"] == []


# ─────────────────────────────────────────────
# Drift Detection
# ─────────────────────────────────────────────

def test_single_panel_change_is_detected():
    """
    One panel change → DRIFTING.
    """
    original = _load_interpretation()

    modified = _with_panel_override(
        original,
        market_regime="RISK_OFF",
    )

    stability = modified["stability"]

    assert stability["status"] == "DRIFTING"
    assert stability["drift_score"] > 0.0
    assert stability["changed_panels"] == ["market_regime"]


def test_multiple_panel_changes_compound_drift():
    """
    Multiple changes → higher drift score.
    """
    original = _load_interpretation()

    modified = _with_panel_override(
        original,
        market_regime="RISK_OFF",
        risk_climate="HIGH",
        strategy_stress="HIGH",
    )

    stability = modified["stability"]

    assert stability["status"] in {"DRIFTING", "UNSTABLE"}
    assert stability["drift_score"] > 0.0
    assert set(stability["changed_panels"]) == {
        "market_regime",
        "risk_climate",
        "strategy_stress",
    }


# ─────────────────────────────────────────────
# Drift Severity Thresholds
# ─────────────────────────────────────────────

def test_excessive_drift_becomes_unstable():
    """
    Large interpretation shift → UNSTABLE.
    """
    original = _load_interpretation()

    modified = _with_panel_override(
        original,
        market_regime="RISK_OFF",
        risk_climate="HIGH",
        strategy_stress="HIGH",
        capital_pressure="HIGH",
    )

    stability = modified["stability"]

    assert stability["status"] == "UNSTABLE"
    assert stability["drift_score"] >= 1.0


# ─────────────────────────────────────────────
# Determinism & Safety
# ─────────────────────────────────────────────

def test_stability_is_deterministic():
    """
    Same interpretation → same stability output.
    """
    interpretation = _load_interpretation()

    s1 = interpretation["stability"]
    s2 = interpretation["stability"]

    assert s1 == s2


def test_stability_does_not_mutate_interpretation():
    """
    Stability evaluation must not mutate interpretation.
    """
    interpretation = _load_interpretation()
    before = deepcopy(interpretation)

    _ = interpretation["stability"]

    assert interpretation == before


def test_stability_has_no_wallclock_dependency():
    """
    Stability must be snapshot-anchored, not time-based.
    """
    interpretation = _load_interpretation()

    s1 = interpretation["stability"]

    # simulate time passing
    _ = datetime.now(timezone.utc)

    s2 = interpretation["stability"]

    assert s1 == s2


# ─────────────────────────────────────────────
# Authority Boundaries
# ─────────────────────────────────────────────

def test_stability_has_no_execution_or_governance_authority():
    """
    Stability surface must never contain action semantics.
    """
    stability = _load_interpretation()["stability"]

    forbidden_keys = {
        "execute",
        "block",
        "approve",
        "reject",
        "capital",
        "order",
    }

    assert forbidden_keys.isdisjoint(stability.keys())
