from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class PromotionReadinessResult:
    """
    Immutable promotion readiness evaluation.

    This object is informational only.
    It does NOT trigger any promotion.
    """

    is_eligible: bool
    reason: str


def evaluate_promotion_readiness(metrics: Dict) -> PromotionReadinessResult:
    """
    Evaluate whether a strategy is eligible
    to be considered for promotion.

    Eligibility rules (v1):
    - SSR >= 0.6
    - trade_count >= 20
    - drawdown_breached == False

    Deterministic. No side effects.
    """

    ssr = float(metrics.get("ssr", 0.0))
    trade_count = int(metrics.get("trade_count", 0))
    drawdown_breached = bool(metrics.get("drawdown_breached", False))

    if ssr < 0.6:
        return PromotionReadinessResult(
            is_eligible=False,
            reason="SSR below eligibility threshold",
        )

    if trade_count < 20:
        return PromotionReadinessResult(
            is_eligible=False,
            reason="Insufficient trade sample size",
        )

    if drawdown_breached:
        return PromotionReadinessResult(
            is_eligible=False,
            reason="Drawdown breach detected",
        )

    return PromotionReadinessResult(
        is_eligible=True,
        reason="Strategy eligible for promotion consideration",
    )
