from typing import List

from core.tournament.paper_contracts import PaperEvaluation
from core.tournament.live_promotion_contracts import (
    LivePromotionDecision,
    LivePromotionThresholds,
)


def evaluate_for_live(
    evaluation: PaperEvaluation,
    thresholds: LivePromotionThresholds,
) -> LivePromotionDecision:
    """
    Phase T-6 gate: Paper -> Live Candidate
    HARD RULES ONLY. No ranking. No overrides.
    """
    reasons: List[str] = []

    if evaluation.paper_ssr < thresholds.min_paper_ssr:
        reasons.append(
            f"Paper SSR below threshold: {evaluation.paper_ssr:.3f} < {thresholds.min_paper_ssr}"
        )

    if evaluation.total_trades < thresholds.min_trades:
        reasons.append(
            f"Insufficient paper trades: {evaluation.total_trades} < {thresholds.min_trades}"
        )

    if evaluation.slippage_pct > thresholds.max_slippage_pct:
        reasons.append(
            f"Slippage too high: {evaluation.slippage_pct:.2f}% > {thresholds.max_slippage_pct}%"
        )

    if evaluation.avg_latency_ms > thresholds.max_latency_ms:
        reasons.append(
            f"Latency too high: {evaluation.avg_latency_ms:.1f}ms > {thresholds.max_latency_ms}ms"
        )

    if evaluation.risk_blocks > thresholds.max_risk_blocks:
        reasons.append(
            f"Risk blocks present: {evaluation.risk_blocks} > {thresholds.max_risk_blocks}"
        )

    promoted = len(reasons) == 0

    return LivePromotionDecision(
        run_id=evaluation.run_id,
        strategy_id=evaluation.strategy_id,
        promoted=promoted,
        reasons=reasons,
    )
