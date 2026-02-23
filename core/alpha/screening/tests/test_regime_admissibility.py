from core.alpha.screening.regime import run_regime_admissibility
from core.alpha.screening.models.screening_layer import ScreeningLayer


def test_high_volatility_regime_fails():
    verdict = run_regime_admissibility(
        symbol="TEST",
        realized_vol=0.60,
        long_run_vol=0.25,
        trend_strength=0.2,
        structural_break=True,
    )

    assert verdict.eligible is False
    assert verdict.failed_layer == ScreeningLayer.REGIME_ADMISSIBILITY

def test_stable_regime_passes():
    verdict = run_regime_admissibility(
        symbol="RELIANCE",
        realized_vol=0.18,
        long_run_vol=0.22,
        trend_strength=0.8,
        structural_break=False,
    )

    assert verdict.eligible is True
    assert verdict.confidence > 0.7

def test_regime_verdict_contains_evidence():
    verdict = run_regime_admissibility(
        symbol="TEST",
        realized_vol=0.30,
        long_run_vol=0.25,
        trend_strength=0.5,
        structural_break=False,
    )

    assert len(verdict.evidence) >= 3
    assert verdict.explanation

