from core.alpha.screening.liquidity import run_liquidity_survivability
from core.alpha.screening.models.screening_layer import ScreeningLayer


def test_illiquid_symbol_fails_liquidity_survivability():
    """
    Illiquid symbol must fail liquidity survivability
    under stressed conditions.
    """
    verdict = run_liquidity_survivability(
        symbol="ILLQ",
        adv_value=5_000_000,        # ₹50L
        order_value=20_000_000,     # ₹2Cr
        volatility_spike=True,
    )

    assert verdict.eligible is False
    assert verdict.failed_layer == ScreeningLayer.LIQUIDITY_SURVIVABILITY
    assert verdict.confidence < 0.5


def test_liquid_symbol_passes_liquidity_survivability():
    """
    Highly liquid symbol must pass liquidity survivability
    under normal conditions.
    """
    verdict = run_liquidity_survivability(
        symbol="RELIANCE",
        adv_value=2_000_000_000,    # ₹200Cr
        order_value=10_000_000,     # ₹1Cr
        volatility_spike=False,
    )

    assert verdict.eligible is True
    assert verdict.failed_layer is None
    assert verdict.confidence > 0.7


def test_liquidity_verdict_contains_evidence():
    """
    Liquidity verdict must always contain
    structured evidence (L3 proof requirement).
    """
    verdict = run_liquidity_survivability(
        symbol="TEST",
        adv_value=500_000_000,      # ₹50Cr
        order_value=5_000_000,      # ₹50L
        volatility_spike=False,
    )

    assert len(verdict.evidence) >= 3
    assert all(e.metric for e in verdict.evidence)
    assert verdict.explanation
