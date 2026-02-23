from dataclasses import dataclass
from typing import List

from core.alpha.screening.models.screening_layer import ScreeningLayer


# -------------------------------------------------
# Evidence model (L3 proof requirement)
# -------------------------------------------------

@dataclass(frozen=True)
class StatisticalEvidence:
    metric: str
    value: float | bool
    threshold: float | None
    passed: bool
    rationale: str


# -------------------------------------------------
# Verdict model
# -------------------------------------------------

@dataclass(frozen=True)
class StatisticalIllusionVerdict:
    symbol: str
    eligible: bool
    confidence: float
    failed_layer: ScreeningLayer | None
    evidence: List[StatisticalEvidence]
    explanation: str


# -------------------------------------------------
# Engine (PURE, DETERMINISTIC)
# -------------------------------------------------

def run_statistical_illusion(
    *,
    symbol: str,
    sample_size: int,
    sharpe: float,
    stability_score: float,
    regime_consistency: bool,
) -> StatisticalIllusionVerdict:
    evidence: List[StatisticalEvidence] = []

    # -------------------------------
    # Rule 1 — Minimum sample size
    # -------------------------------
    min_samples = 200
    sample_pass = sample_size >= min_samples

    evidence.append(
        StatisticalEvidence(
            metric="sample_size",
            value=sample_size,
            threshold=min_samples,
            passed=sample_pass,
            rationale="Reject low-sample statistical illusions",
        )
    )

    # -------------------------------
    # Rule 2 — Stability score
    # -------------------------------
    min_stability = 0.6
    stability_pass = stability_score >= min_stability

    evidence.append(
        StatisticalEvidence(
            metric="stability_score",
            value=stability_score,
            threshold=min_stability,
            passed=stability_pass,
            rationale="Reject unstable performance profiles",
        )
    )

    # -------------------------------
    # Rule 3 — Regime consistency
    # -------------------------------
    evidence.append(
        StatisticalEvidence(
            metric="regime_consistency",
            value=regime_consistency,
            threshold=None,
            passed=regime_consistency,
            rationale="Reject regime-dependent illusions",
        )
    )

    # -------------------------------
    # Final verdict
    # -------------------------------
    passed_all = all(e.passed for e in evidence)

    if not passed_all:
        return StatisticalIllusionVerdict(
            symbol=symbol,
            eligible=False,
            confidence=0.0,
            failed_layer=ScreeningLayer.STATISTICAL_ILLUSION,
            evidence=evidence,
            explanation="Statistical illusion detected — signal rejected",
        )

    confidence = round(
        min(
            1.0,
            (stability_score + min(sharpe / 2.0, 1.0)) / 2,
        ),
        3,
    )

    return StatisticalIllusionVerdict(
        symbol=symbol,
        eligible=True,
        confidence=confidence,
        failed_layer=None,
        evidence=evidence,
        explanation="Signal passes statistical robustness checks",
    )
