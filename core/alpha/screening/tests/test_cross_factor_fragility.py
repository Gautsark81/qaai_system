from core.alpha.screening.cross_factor_fragility import (
    run_cross_factor_fragility,
)
from core.alpha.screening.models.screening_layer import ScreeningLayer


def test_hidden_market_beta_fails_fragility():
    verdict = run_cross_factor_fragility(
        symbol="FAKE_ALPHA",
        factor_exposures={
            "market_beta": 0.92,
            "sector_energy": 0.85,
            "momentum": 0.30,
        },
    )

    assert verdict.eligible is False
    assert verdict.failed_layer == ScreeningLayer.CROSS_FACTOR_FRAGILITY


def test_diversified_factor_profile_passes_fragility():
    verdict = run_cross_factor_fragility(
        symbol="ROBUST_ALPHA",
        factor_exposures={
            "market_beta": 0.25,
            "sector_energy": 0.10,
            "momentum": 0.35,
            "value": 0.40,
        },
    )

    assert verdict.eligible is True
    assert verdict.confidence > 0.7


def test_fragility_verdict_contains_evidence():
    verdict = run_cross_factor_fragility(
        symbol="CHECK_EVIDENCE",
        factor_exposures={
            "market_beta": 0.6,
            "momentum": 0.7,
        },
    )

    assert len(verdict.evidence) >= 3
    assert all(e.metric for e in verdict.evidence)
