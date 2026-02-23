from dataclasses import dataclass

from .snapshot import EnsembleSnapshot
from .shadow_ml import ShadowMLComparator
from .allocator import EnsembleAllocator


@dataclass(frozen=True)
class MLGuardrailResult:
    ml_allowed: bool
    total_drift_pct: float
    max_single_drift_pct: float


class MLDriftGuardrail:

    @staticmethod
    def evaluate(snapshot: EnsembleSnapshot) -> MLGuardrailResult:

        if not snapshot.meta_ml_enabled:
            return MLGuardrailResult(
                ml_allowed=False,
                total_drift_pct=0.0,
                max_single_drift_pct=0.0,
            )

        comparison = ShadowMLComparator.compare(snapshot)

        total_drift_pct = (
            comparison.total_drift / snapshot.available_capital
            if snapshot.available_capital > 0
            else 0.0
        )

        max_single_drift_pct = (
            comparison.max_single_strategy_drift / snapshot.available_capital
            if snapshot.available_capital > 0
            else 0.0
        )

        allowed = (
            total_drift_pct <= snapshot.meta_ml_max_total_drift_pct
            and max_single_drift_pct <= snapshot.meta_ml_max_single_drift_pct
        )

        return MLGuardrailResult(
            ml_allowed=allowed,
            total_drift_pct=total_drift_pct,
            max_single_drift_pct=max_single_drift_pct,
        )

    @staticmethod
    def safe_allocate(snapshot: EnsembleSnapshot):
        """
        Returns safe allocation result.
        If ML drift exceeds thresholds, fallback to baseline.
        """
        guard = MLDriftGuardrail.evaluate(snapshot)

        if not guard.ml_allowed:
            # Force ML disabled
            safe_snapshot = EnsembleSnapshot(
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
            )
            return EnsembleAllocator.allocate(safe_snapshot)

        return EnsembleAllocator.allocate(snapshot)