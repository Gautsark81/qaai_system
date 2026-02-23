# core/tournament/promotion_gate.py

from typing import List

from core.tournament.metrics_contract import StrategyMetrics
from core.tournament.promotion_contracts import (
    PromotionDecision,
    PromotionThresholds,
)


def evaluate_for_paper(
    metrics: StrategyMetrics,
    thresholds: PromotionThresholds,
) -> PromotionDecision:
    """
    Phase T-4 Promotion Gate (Backtest → Paper)

    HARD RULES ONLY.
    No ranking. No heuristics. No overrides.
    """

    reasons: List[str] = []

    if metrics.ssr < thresholds.min_ssr:
        reasons.append(
            f"SSR below threshold: {metrics.ssr:.3f} < {thresholds.min_ssr}"
        )

    if metrics.total_trades < thresholds.min_trades:
        reasons.append(
            f"Insufficient trades: {metrics.total_trades} < {thresholds.min_trades}"
        )

    if metrics.max_drawdown_pct > thresholds.max_drawdown_pct:
        reasons.append(
            f"Max drawdown too high: {metrics.max_drawdown_pct:.2f}% > {thresholds.max_drawdown_pct}%"
        )

    if metrics.max_single_loss_pct > thresholds.max_single_loss_pct:
        reasons.append(
            f"Max single loss too high: {metrics.max_single_loss_pct:.2f}% > {thresholds.max_single_loss_pct}%"
        )

    promoted = len(reasons) == 0

    return PromotionDecision(
        strategy_id=metrics.strategy_id,
        promoted=promoted,
        reasons=reasons,
    )
