# tests/dashboard/phase7/test_phase7_cross_panel_consistency.py

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
    Create a modified interpretation with specific panel labels overridden.
    This must NOT mutate the original interpretation.
    """
    cloned = deepcopy(interpretation)

    for panel_name, label in overrides.items():
        assert panel_name in cloned, f"Unknown panel: {panel_name}"
        cloned[panel_name]["label"] = label

    return cloned


# ─────────────────────────────────────────────
# Core Presence & Shape
# ─────────────────────────────────────────────

def test_consistency_section_is_present():
    """
    Phase-7.2 must expose a consistency surface.
    """
    interpretation = _load_interpretation()

    assert "consistency" in interpretation
    consistency = interpretation["consistency"]

    assert isinstance(consistency, dict)
    assert "status" in consistency
    assert "violations" in consistency
    assert "confidence_impact" in consistency


def test_default_consistency_is_consistent():
    """
    Default snapshot should not contain contradictions.
    """
    interpretation = _load_interpretation()
    consistency = interpretation["consistency"]

    assert consistency["status"] == "CONSISTENT"
    assert consistency["violations"] == []
    assert consistency["confidence_impact"] == 0.0


# ─────────────────────────────────────────────
# Rule C-1 — Risk vs Regime
# ─────────────────────────────────────────────

def test_contradiction_risk_off_with_low_risk_climate():
    """
    market_regime = RISK_OFF
    risk_climate  = LOW
    → contradiction
    """
    interpretation = _load_interpretation()

    modified = _with_panel_override(
        interpretation,
        market_regime="RISK_OFF",
        risk_climate="LOW",
    )

    consistency = modified["consistency"]

    assert consistency["status"] == "CONTRADICTORY"
    assert len(consistency["violations"]) == 1

    violation = consistency["violations"][0]
    assert violation["rule_id"] == "C-1"
    assert set(violation["panels"]) == {"market_regime", "risk_climate"}


# ─────────────────────────────────────────────
# Rule C-2 — Stress vs Capital
# ─────────────────────────────────────────────

def test_contradiction_high_stress_with_low_capital_pressure():
    """
    strategy_stress = HIGH
    capital_pressure = LOW
    → contradiction
    """
    interpretation = _load_interpretation()

    modified = _with_panel_override(
        interpretation,
        strategy_stress="HIGH",
        capital_pressure="LOW",
    )

    consistency = modified["consistency"]

    assert consistency["status"] == "CONTRADICTORY"
    assert len(consistency["violations"]) == 1

    violation = consistency["violations"][0]
    assert violation["rule_id"] == "C-2"
    assert set(violation["panels"]) == {"strategy_stress", "capital_pressure"}


# ─────────────────────────────────────────────
# Rule C-3 — Calm Paradox
# ─────────────────────────────────────────────

def test_contradiction_calm_market_with_high_risk_climate():
    """
    market_regime = CALM
    risk_climate  = HIGH
    → contradiction
    """
    interpretation = _load_interpretation()

    modified = _with_panel_override(
        interpretation,
        market_regime="CALM",
        risk_climate="HIGH",
    )

    consistency = modified["consistency"]

    assert consistency["status"] == "CONTRADICTORY"
    assert len(consistency["violations"]) == 1

    violation = consistency["violations"][0]
    assert violation["rule_id"] == "C-3"
    assert set(violation["panels"]) == {"market_regime", "risk_climate"}


# ─────────────────────────────────────────────
# Multiple Contradictions
# ─────────────────────────────────────────────

def test_multiple_contradictions_are_all_reported():
    """
    System must surface ALL contradictions, not just the first.
    """
    interpretation = _load_interpretation()

    modified = _with_panel_override(
        interpretation,
        market_regime="RISK_OFF",
        risk_climate="LOW",
        strategy_stress="HIGH",
        capital_pressure="LOW",
    )

    consistency = modified["consistency"]

    assert consistency["status"] == "CONTRADICTORY"
    assert len(consistency["violations"]) == 2

    rule_ids = {v["rule_id"] for v in consistency["violations"]}
    assert rule_ids == {"C-1", "C-2"}


# ─────────────────────────────────────────────
# Determinism & Safety
# ─────────────────────────────────────────────

def test_consistency_is_deterministic_for_same_interpretation():
    """
    Same interpretation → same consistency output.
    """
    interpretation = _load_interpretation()

    c1 = interpretation["consistency"]
    c2 = interpretation["consistency"]

    assert c1 == c2


def test_consistency_does_not_mutate_interpretation():
    """
    Consistency evaluation must not mutate panels.
    """
    interpretation = _load_interpretation()
    before = deepcopy(interpretation)

    _ = interpretation["consistency"]

    assert interpretation == before


def test_consistency_has_no_wallclock_dependency():
    """
    Consistency evaluation must not depend on wall-clock time.
    """
    interpretation = _load_interpretation()

    c1 = interpretation["consistency"]

    # simulate time passage
    future = datetime.now(timezone.utc)

    c2 = interpretation["consistency"]

    assert c1 == c2
