from dataclasses import dataclass
from typing import Dict

from .models import AllocationResult
from .snapshot import EnsembleSnapshot
from .meta_ml_advisor import MetaMLAdvisor


@dataclass(frozen=True)
class MetaScoreResult:
    scores: Dict[str, float]


class MetaAlphaCalculator:

    @staticmethod
    def calculate(
        snapshot: EnsembleSnapshot,
        result: AllocationResult,
    ) -> MetaScoreResult:

        deployed_capital = sum(result.allocations.values())
        base_scores: Dict[str, float] = {}

        for strategy in snapshot.strategies:

            sid = strategy.strategy_id
            allocation = result.allocations.get(sid, 0.0)
            governance_adj = result.governance_adjustments.get(sid, 0.0)

            # ----------------------------
            # Component Scores
            # ----------------------------

            # SSR component
            ssr_score = strategy.ssr / 100.0

            # Drawdown stability
            drawdown_score = 1 - (strategy.drawdown_pct / 100.0)

            # Capital efficiency
            capital_efficiency = (
                allocation / snapshot.available_capital
                if snapshot.available_capital > 0
                else 0.0
            )

            # Governance shrink score
            if allocation > 0:
                governance_score = 1 - (governance_adj / allocation)
            else:
                governance_score = 0.0

            # Concentration penalty
            if deployed_capital > 0 and allocation > 0:
                concentration_ratio = allocation / deployed_capital
                concentration_score = 0.8 if concentration_ratio > 0.5 else 1.0
            else:
                concentration_score = 0.0

            # ----------------------------
            # Adaptive Weighted MetaScore (C8.3)
            # ----------------------------
            meta_score = (
                snapshot.meta_ssr_weight * ssr_score
                + snapshot.meta_drawdown_weight * drawdown_score
                + snapshot.meta_capital_eff_weight * capital_efficiency
                + snapshot.meta_governance_weight * governance_score
                + snapshot.meta_concentration_weight * concentration_score
            )

            base_scores[sid] = meta_score

        # ----------------------------
        # C8.4 Advisory ML Adjustment
        # ----------------------------
        ml_result = MetaMLAdvisor.calculate(snapshot, result, base_scores)

        adjusted_scores: Dict[str, float] = {}

        for sid, base_score in base_scores.items():
            delta = ml_result.deltas.get(sid, 0.0)
            adjusted_scores[sid] = base_score + delta

        return MetaScoreResult(scores=adjusted_scores)