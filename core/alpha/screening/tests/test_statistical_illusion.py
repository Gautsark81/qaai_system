from core.alpha.screening.statistical_illusion import run_statistical_illusion
from core.alpha.screening.models.screening_layer import ScreeningLayer


def test_low_sample_size_fails():
    verdict = run_statistical_illusion(
        symbol="ILLUSION",
        sample_size=25,
        sharpe=2.1,
        stability_score=0.4,
        regime_consistency=False,
    )

    assert verdict.eligible is False
    assert verdict.failed_layer == ScreeningLayer.STATISTICAL_ILLUSION

def test_robust_signal_passes():
    verdict = run_statistical_illusion(
        symbol="ROBUST",
        sample_size=800,
        sharpe=1.4,
        stability_score=0.85,
        regime_consistency=True,
    )

    assert verdict.eligible is True
    assert verdict.confidence > 0.7

def test_statistical_illusion_verdict_contains_evidence():
    verdict = run_statistical_illusion(
        symbol="TEST",
        sample_size=300,
        sharpe=1.2,
        stability_score=0.6,
        regime_consistency=True,
    )

    assert len(verdict.evidence) >= 3
    assert verdict.explanation
