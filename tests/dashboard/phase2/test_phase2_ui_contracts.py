# tests/dashboard/phase2/test_phase2_ui_contracts.py

import pytest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

from dashboard.snapshot_loader import load_dashboard_snapshot


# ─────────────────────────────────────────────
# Phase-2.0A — UI CONTRACTS & INVARIANTS
# TESTS ONLY — NO IMPLEMENTATION
# ─────────────────────────────────────────────


def test_phase2_snapshot_exposes_interpretation_surface():
    """
    Phase-2 may EXPLAIN system state.
    It may never mutate or command it.
    """
    _, snapshot = load_dashboard_snapshot()

    assert hasattr(snapshot, "interpretation"), \
        "Phase-2 must expose interpretation surface"

    interpretation = snapshot.interpretation

    assert isinstance(interpretation, dict)
    assert "market_regime" in interpretation
    assert "risk_climate" in interpretation
    assert "strategy_stress" in interpretation
    assert "capital_pressure" in interpretation


def test_interpretation_is_read_only():
    """
    Interpretation surface must be immutable.
    """
    _, snapshot = load_dashboard_snapshot()

    with pytest.raises(FrozenInstanceError):
        snapshot.interpretation["market_regime"] = "RISK_ON"


def test_phase2_never_exposes_execution_controls():
    """
    Phase-2 UI must NEVER expose execution, arming, or scheduling.
    """
    _, snapshot = load_dashboard_snapshot()

    forbidden = [
        "execute",
        "arm",
        "deploy",
        "schedule",
        "override",
        "run_now",
        "force_trade",
    ]

    for attr in forbidden:
        assert not hasattr(snapshot, attr), f"Forbidden capability leaked: {attr}"


def test_phase2_never_exposes_capital_controls():
    """
    Capital math and allocation are forbidden in Phase-2 UI.
    """
    _, snapshot = load_dashboard_snapshot()

    forbidden = [
        "allocate_capital",
        "rebalance",
        "position_size",
        "exposure_adjust",
        "risk_budget",
    ]

    for attr in forbidden:
        assert not hasattr(snapshot, attr), f"Capital control leaked: {attr}"


def test_phase2_interpretation_is_snapshot_derived_only():
    """
    Interpretation must be derived ONLY from snapshot,
    never from live feeds or mutable state.
    """
    _, snapshot = load_dashboard_snapshot()

    interpretation = snapshot.interpretation

    assert interpretation["derived_from"] == snapshot.hash
    assert interpretation["timestamp"] <= datetime.now(timezone.utc)


def test_phase2_interpretation_contains_uncertainty_language():
    """
    Every interpretation must acknowledge uncertainty.
    """
    _, snapshot = load_dashboard_snapshot()

    interpretation = snapshot.interpretation

    for key, section in interpretation.items():
        if isinstance(section, dict):
            assert "confidence" in section
            assert 0.0 <= section["confidence"] <= 1.0
            assert "uncertainty_note" in section
            assert isinstance(section["uncertainty_note"], str)
            assert len(section["uncertainty_note"]) > 0


def test_phase2_governance_actions_are_record_only():
    """
    Phase-2 may RECORD human judgment.
    It may never execute it.
    """
    _, snapshot = load_dashboard_snapshot()

    assert hasattr(snapshot, "record_governance_decision")

    decision = snapshot.record_governance_decision(
        status="HOLD",
        reason="Unclear regime transition",
        severity="MEDIUM",
    )

    assert decision.snapshot_hash == snapshot.hash
    assert decision.is_binding is False


def test_phase2_governance_decision_is_immutable():
    """
    Governance records must be immutable.
    """
    _, snapshot = load_dashboard_snapshot()

    decision = snapshot.record_governance_decision(
        status="REJECT",
        reason="Risk escalation",
        severity="HIGH",
    )

    with pytest.raises(FrozenInstanceError):
        decision.status = "APPROVED"


def test_phase2_refuses_one_click_actions():
    """
    Explicitly ban dangerous UX patterns.
    """
    _, snapshot = load_dashboard_snapshot()

    banned_phrases = [
        "one_click",
        "quick_approve",
        "approve_and_execute",
        "auto_fix",
    ]

    for phrase in banned_phrases:
        assert phrase not in dir(snapshot), f"Banned UX primitive found: {phrase}"
