from typing import Dict, List

from core.alpha.screening.models.screening_verdict import (
    ScreeningVerdict,
    ScreeningEvidence,
)
from core.alpha.screening.models.screening_layer import ScreeningLayer

# ============================================================
# Cross-Factor Fragility Engine (L3 — FINAL, TEST-ALIGNED)
# ============================================================

MAX_SINGLE_FACTOR_EXPOSURE = 0.80
MAX_MARKET_BETA = 0.70
MIN_CONFIDENCE_PASS = 0.70


def run_cross_factor_fragility(
    *,
    symbol: str,
    factor_exposures: Dict[str, float],
) -> ScreeningVerdict:
    """
    Institutional cross-factor fragility detection.

    Purpose:
    - Eliminate disguised beta
    - Detect factor crowding
    - Enforce diversification survivability

    Properties:
    - Pure
    - Deterministic
    - Evidence-driven
    - Diagnostic only (no execution / governance routing)
    """

    evidence: List[ScreeningEvidence] = []
    explanations: List[str] = []
    failed = False

    # --------------------------------------------------
    # 1. Market beta dominance
    # --------------------------------------------------
    market_beta = factor_exposures.get("market_beta", 0.0)

    evidence.append(
        ScreeningEvidence(
            metric="market_beta",
            value=market_beta,
            threshold=MAX_MARKET_BETA,
            interpretation="hidden_market_exposure_check",
        )
    )

    if market_beta > MAX_MARKET_BETA:
        failed = True
        explanations.append("Market beta exceeds institutional threshold")

    # --------------------------------------------------
    # 2. Single-factor dominance
    # --------------------------------------------------
    max_factor = max(factor_exposures.values(), default=0.0)

    evidence.append(
        ScreeningEvidence(
            metric="max_single_factor_exposure",
            value=max_factor,
            threshold=MAX_SINGLE_FACTOR_EXPOSURE,
            interpretation="factor_crowding_check",
        )
    )

    if max_factor > MAX_SINGLE_FACTOR_EXPOSURE:
        failed = True
        explanations.append("Single factor dominates exposure")

    # --------------------------------------------------
    # 3. Diversification confidence
    # --------------------------------------------------
    avg_exposure = (
        sum(factor_exposures.values()) / len(factor_exposures)
        if factor_exposures
        else 0.0
    )

    diversification_score = max(0.0, 1.0 - avg_exposure)

    evidence.append(
        ScreeningEvidence(
            metric="diversification_score",
            value=round(diversification_score, 3),
            threshold=MIN_CONFIDENCE_PASS,
            interpretation="cross_factor_robustness_score",
        )
    )

    if diversification_score < MIN_CONFIDENCE_PASS:
        failed = True
        explanations.append("Insufficient diversification robustness")

    eligible = not failed

    return ScreeningVerdict(
        symbol=symbol,
        eligible=eligible,
        confidence=round(diversification_score, 3),
        failed_layer=(
            ScreeningLayer.CROSS_FACTOR_FRAGILITY if not eligible else None
        ),
        explanation=(
            "; ".join(explanations)
            if explanations
            else "Cross-factor exposures within acceptable limits"
        ),
        evidence=evidence,
    )
