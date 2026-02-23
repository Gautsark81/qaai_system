from dataclasses import dataclass
from typing import List

from .snapshot import EnsembleSnapshot
from .ml_promotion import MLPromotionEngine, MLPromotionDecision
from .ml_guardrail import MLDriftGuardrail
from .shadow_performance import ShadowPerformanceResult
from .allocator import EnsembleAllocator


@dataclass(frozen=True)
class MLLifecycleStatus:
    promotion_status: str  # PROMOTE / ADVISORY / DEMOTE
    drift_allowed: bool
    final_allocation_source: str  # BASELINE / ML
    avg_return_delta: float
    avg_drawdown_delta: float


class MLLifecycleManager:

    @staticmethod
    def evaluate(
        snapshot: EnsembleSnapshot,
        performance_history: List[ShadowPerformanceResult],
    ) -> MLLifecycleStatus:

        # 1️⃣ Evaluate promotion decision
        promotion = MLPromotionEngine.evaluate(
            snapshot,
            performance_history,
        )

        # 2️⃣ Evaluate drift guardrail
        drift = MLDriftGuardrail.evaluate(snapshot)

        # 3️⃣ Determine final allocation authority
        if promotion.status == "PROMOTE" and drift.ml_allowed:
            source = "ML"
        else:
            source = "BASELINE"

        return MLLifecycleStatus(
            promotion_status=promotion.status,
            drift_allowed=drift.ml_allowed,
            final_allocation_source=source,
            avg_return_delta=promotion.avg_return_delta,
            avg_drawdown_delta=promotion.avg_drawdown_delta,
        )

    @staticmethod
    def allocate_with_governance(
        snapshot: EnsembleSnapshot,
        performance_history: List[ShadowPerformanceResult],
    ):
        status = MLLifecycleManager.evaluate(
            snapshot,
            performance_history,
        )

        if status.final_allocation_source == "ML":
            return EnsembleAllocator.allocate(snapshot)

        # Force baseline allocation
        baseline_snapshot = EnsembleSnapshot(
            strategies=snapshot.strategies,
            available_capital=snapshot.available_capital,
            global_cap=snapshot.global_cap,
            per_strategy_cap=snapshot.per_strategy_cap,
            concentration_cap=snapshot.concentration_cap,
            suspension_drawdown_pct=snapshot.suspension_drawdown_pct,
            suspension_min_ssr=snapshot.suspension_min_ssr,
            meta_ssr_weight=snapshot.meta_ssr_weight,
            meta_drawdown_weight=snapshot.meta_drawdown_weight,
            meta_capital_eff_weight=snapshot.meta_capital_eff_weight,
            meta_governance_weight=snapshot.meta_governance_weight,
            meta_concentration_weight=snapshot.meta_concentration_weight,
            meta_ml_enabled=False,
            meta_ml_max_total_drift_pct=snapshot.meta_ml_max_total_drift_pct,
            meta_ml_max_single_drift_pct=snapshot.meta_ml_max_single_drift_pct,
            meta_ml_min_return_delta=snapshot.meta_ml_min_return_delta,
            meta_ml_max_drawdown_delta=snapshot.meta_ml_max_drawdown_delta,
            meta_ml_required_shadow_cycles=snapshot.meta_ml_required_shadow_cycles,
        )

        return EnsembleAllocator.allocate(baseline_snapshot)