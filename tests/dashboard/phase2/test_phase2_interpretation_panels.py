import pytest
from datetime import datetime, timezone
from dataclasses import FrozenInstanceError

from dashboard.snapshot_loader import load_dashboard_snapshot


# ─────────────────────────────────────────────
# Phase-2.1A — Interpretation Panels Contract
# ─────────────────────────────────────────────


def test_snapshot_exposes_interpretation_panels():
    """
    Phase-2.1 must expose interpretation panels.
    These explain system state — never actions.
    """
    _, snapshot = load_dashboard_snapshot()

    interpretation = snapshot.interpretation

    assert isinstance(interpretation, dict)

    # Required panels
    assert "market_regime" in interpretation
    assert "risk_climate" in interpretation
    assert "strategy_stress" in interpretation
    assert "capital_pressure" in interpretation


def test_interpretation_panels_are_snapshot_derived_only():
    """
    Interpretation must be derived strictly from snapshot.
    No live feeds. No mutable state.
    """
    _, snapshot = load_dashboard_snapshot()
    interpretation = snapshot.interpretation

    assert interpretation["derived_from"] == snapshot.hash
    assert isinstance(interpretation["timestamp"], datetime)
    assert interpretation["timestamp"] <= datetime.now(timezone.utc)


def test_interpretation_panels_are_read_only():
    """
    Interpretation panels must be immutable.
    """
    _, snapshot = load_dashboard_snapshot()
    interpretation = snapshot.interpretation

    with pytest.raises(FrozenInstanceError):
        interpretation["market_regime"] = "RISK_ON"


def test_interpretation_panels_include_uncertainty_language():
    """
    Every interpretation must explicitly acknowledge uncertainty.
    """
    _, snapshot = load_dashboard_snapshot()
    interpretation = snapshot.interpretation

    uncertainty = interpretation.get("uncertainty_note")
    assert isinstance(uncertainty, str)
    assert len(uncertainty.strip()) > 0


def test_interpretation_panels_are_confidence_scored():
    """
    Interpretations must expose confidence, never certainty.
    """
    _, snapshot = load_dashboard_snapshot()
    interpretation = snapshot.interpretation

    confidence = interpretation.get("confidence")
    assert isinstance(confidence, float)
    assert 0.0 <= confidence <= 1.0


def test_interpretation_contains_no_actionable_fields():
    """
    Phase-2.1 must never suggest actions or commands.
    """
    _, snapshot = load_dashboard_snapshot()
    interpretation = snapshot.interpretation

    banned_fields = {
        "execute",
        "deploy",
        "approve",
        "reject",
        "arm",
        "disarm",
        "capital_change",
        "strategy_toggle",
    }

    for field in banned_fields:
        assert field not in interpretation


def test_interpretation_does_not_modify_snapshot_state():
    """
    Reading interpretation must not mutate snapshot.
    """
    _, snapshot = load_dashboard_snapshot()

    _ = snapshot.interpretation

    with pytest.raises(TypeError):
        snapshot.parent_hash = "tamper"


def test_interpretation_is_deterministic_for_same_snapshot():
    """
    Same snapshot → same interpretation.
    """
    _, s1 = load_dashboard_snapshot()
    _, s2 = load_dashboard_snapshot()

    assert s1.hash == s2.hash
    assert s1.interpretation == s2.interpretation


def test_interpretation_panels_are_present_even_with_minimal_data():
    """
    Interpretation must exist even when signals are sparse.
    """
    _, snapshot = load_dashboard_snapshot()
    interpretation = snapshot.interpretation

    for key in (
        "market_regime",
        "risk_climate",
        "strategy_stress",
        "capital_pressure",
    ):
        assert interpretation[key] is not None
