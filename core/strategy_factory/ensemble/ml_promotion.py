from dataclasses import dataclass
from typing import List

from .snapshot import EnsembleSnapshot
from .shadow_performance import ShadowPerformanceResult


@dataclass(frozen=True)
class MLPromotionDecision:
    status: str  # "PROMOTE", "ADVISORY", "DEMOTE"
    avg_return_delta: float
    avg_drawdown_delta: float
    cycles_evaluated: int


class MLPromotionEngine:

    @staticmethod
    def evaluate(
        snapshot: EnsembleSnapshot,
        performance_history: List[ShadowPerformanceResult],
    ) -> MLPromotionDecision:

        if not performance_history:
            return MLPromotionDecision(
                status="ADVISORY",
                avg_return_delta=0.0,
                avg_drawdown_delta=0.0,
                cycles_evaluated=0,
            )

        avg_return_delta = sum(
            p.return_delta for p in performance_history
        ) / len(performance_history)

        avg_drawdown_delta = sum(
            p.drawdown_delta for p in performance_history
        ) / len(performance_history)

        cycles = len(performance_history)

        # Promotion rule
        if (
            cycles >= snapshot.meta_ml_required_shadow_cycles
            and avg_return_delta >= snapshot.meta_ml_min_return_delta
            and avg_drawdown_delta <= snapshot.meta_ml_max_drawdown_delta
        ):
            return MLPromotionDecision(
                status="PROMOTE",
                avg_return_delta=avg_return_delta,
                avg_drawdown_delta=avg_drawdown_delta,
                cycles_evaluated=cycles,
            )

        # Demotion rule
        if avg_return_delta < 0:
            return MLPromotionDecision(
                status="DEMOTE",
                avg_return_delta=avg_return_delta,
                avg_drawdown_delta=avg_drawdown_delta,
                cycles_evaluated=cycles,
            )

        return MLPromotionDecision(
            status="ADVISORY",
            avg_return_delta=avg_return_delta,
            avg_drawdown_delta=avg_drawdown_delta,
            cycles_evaluated=cycles,
        )