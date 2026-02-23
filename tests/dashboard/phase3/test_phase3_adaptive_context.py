import pytest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

from dashboard.snapshot_loader import load_dashboard_snapshot


# ─────────────────────────────────────────────
# Phase-3.0 — Adaptive Context (TEST CONTRACT)
# ─────────────────────────────────────────────


def test_snapshot_exposes_adaptive_context_surface():
    """
    Phase-3 must expose an adaptive context surface.
    This surface is READ-ONLY and advisory only.
    """
    _, snapshot = load_dashboard_snapshot()

    assert hasattr(snapshot, "adaptive_context"), (
        "Snapshot must expose adaptive_context surface"
    )


def test_adaptive_context_is_read_only():
    """
    Adaptive context must be immutable.
    """
    _, snapshot = load_dashboard_snapshot()

    context = snapshot.adaptive_context

    with pytest.raises(FrozenInstanceError):
        context["market_regime"] = "RISK_ON"


def test_adaptive_context_is_snapshot_derived_only():
    """
    Adaptive context must be derived ONLY from snapshot.
    No live feeds, no mutable state.
    """
    _, snapshot = load_dashboard_snapshot()

    context = snapshot.adaptive_context

    assert context["derived_from"] == snapshot.hash
    assert context["timestamp"] <= datetime.now(timezone.utc)


def test_adaptive_context_contains_market_regime_band():
    """
    Adaptive context may describe market regime,
    but never predict actions.
    """
    _, snapshot = load_dashboard_snapshot()

    context = snapshot.adaptive_context

    assert context["market_regime"] in {
        "RISK_ON",
        "RISK_OFF",
        "TRANSITION",
        "UNKNOWN",
    }


def test_adaptive_context_contains_volatility_climate():
    """
    Adaptive context must include volatility climate.
    """
    _, snapshot = load_dashboard_snapshot()

    context = snapshot.adaptive_context

    assert context["volatility_climate"] in {
        "LOW",
        "MEDIUM",
        "HIGH",
        "UNKNOWN",
    }


def test_adaptive_context_contains_liquidity_stress_band():
    """
    Adaptive context must include liquidity stress band.
    """
    _, snapshot = load_dashboard_snapshot()

    context = snapshot.adaptive_context

    assert context["liquidity_stress"] in {
        "LOW",
        "MEDIUM",
        "HIGH",
        "UNKNOWN",
    }


def test_adaptive_context_contains_cross_strategy_pressure():
    """
    Adaptive context must describe cross-strategy interaction pressure,
    without recommending changes.
    """
    _, snapshot = load_dashboard_snapshot()

    context = snapshot.adaptive_context

    assert context["strategy_interaction_pressure"] in {
        "LOW",
        "MEDIUM",
        "HIGH",
        "UNKNOWN",
    }


def test_adaptive_context_includes_confidence_and_uncertainty():
    """
    Every adaptive interpretation must expose uncertainty.
    """
    _, snapshot = load_dashboard_snapshot()

    context = snapshot.adaptive_context

    assert 0.0 <= context["confidence"] <= 1.0
    assert isinstance(context["uncertainty_note"], str)
    assert len(context["uncertainty_note"]) > 0


def test_adaptive_context_is_non_binding():
    """
    Adaptive context must never carry authority.
    """
    _, snapshot = load_dashboard_snapshot()

    context = snapshot.adaptive_context

    assert context["is_advisory"] is True
    assert context["can_trigger_actions"] is False


def test_adaptive_context_does_not_modify_snapshot():
    """
    Accessing adaptive context must not mutate snapshot state.
    """
    _, snapshot = load_dashboard_snapshot()
    original_hash = snapshot.hash

    _ = snapshot.adaptive_context

    assert snapshot.hash == original_hash
