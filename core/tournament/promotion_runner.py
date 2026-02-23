# core/tournament/promotion_runner.py

from typing import Iterable, List

from core.tournament.metrics_contract import StrategyMetrics
from core.tournament.promotion_contracts import (
    PromotionDecision,
    PromotionThresholds,
)
from core.tournament.promotion_gate import evaluate_for_paper


def evaluate_strategies_for_paper(
    metrics_list: Iterable[StrategyMetrics],
    thresholds: PromotionThresholds | None = None,
) -> List[PromotionDecision]:

    thresholds = thresholds or PromotionThresholds()

    decisions: List[PromotionDecision] = []

    for metrics in metrics_list:
        decision = evaluate_for_paper(metrics, thresholds)
        decisions.append(decision)

    return decisions
