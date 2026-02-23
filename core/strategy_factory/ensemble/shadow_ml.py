from dataclasses import dataclass
from typing import Dict

from .snapshot import EnsembleSnapshot
from .allocator import EnsembleAllocator


@dataclass(frozen=True)
class ShadowComparisonResult:
    baseline_allocations: Dict[str, float]
    ml_allocations: Dict[str, float]
    allocation_drift: Dict[str, float]
    total_drift: float
    max_single_strategy_drift: float


class ShadowMLComparator:

    @staticmethod
    def compare(snapshot: EnsembleSnapshot) -> ShadowComparisonResult:
        # ----------------------------
        # Baseline (ML Disabled)
        # ----------------------------
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
            meta_ml_enabled=False,  # force OFF
        )

        baseline_result = EnsembleAllocator.allocate(baseline_snapshot)

        # ----------------------------
        # ML Enabled
        # ----------------------------
        ml_snapshot = EnsembleSnapshot(
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
            meta_ml_enabled=True,  # force ON
        )

        ml_result = EnsembleAllocator.allocate(ml_snapshot)

        # ----------------------------
        # Drift Calculation
        # ----------------------------
        drift: Dict[str, float] = {}
        total_drift = 0.0
        max_single_drift = 0.0

        all_keys = set(baseline_result.allocations.keys()).union(
            ml_result.allocations.keys()
        )

        for sid in all_keys:
            base_val = baseline_result.allocations.get(sid, 0.0)
            ml_val = ml_result.allocations.get(sid, 0.0)

            diff = ml_val - base_val
            drift[sid] = diff

            abs_diff = abs(diff)
            total_drift += abs_diff
            max_single_drift = max(max_single_drift, abs_diff)

        return ShadowComparisonResult(
            baseline_allocations=baseline_result.allocations,
            ml_allocations=ml_result.allocations,
            allocation_drift=drift,
            total_drift=total_drift,
            max_single_strategy_drift=max_single_drift,
        )