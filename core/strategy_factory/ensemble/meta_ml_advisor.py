from dataclasses import dataclass
from typing import Dict

from .models import AllocationResult
from .snapshot import EnsembleSnapshot


@dataclass(frozen=True)
class MLAdvisoryResult:
    deltas: Dict[str, float]


class MetaMLAdvisor:

    MAX_DELTA = 0.05  # ±5% cap

    @staticmethod
    def calculate(
        snapshot: EnsembleSnapshot,
        result: AllocationResult,
        base_scores: Dict[str, float],
    ) -> MLAdvisoryResult:

        if not getattr(snapshot, "meta_ml_enabled", False):
            return MLAdvisoryResult(deltas={sid: 0.0 for sid in base_scores})

        deltas = {}

        for strategy in snapshot.strategies:
            sid = strategy.strategy_id
            base_score = base_scores.get(sid, 0.0)

            # Simple deterministic heuristic model (placeholder)
            # Higher SSR + lower drawdown = positive delta
            signal = (
                (strategy.ssr / 100.0)
                - (strategy.drawdown_pct / 100.0)
            )

            delta = signal * 0.02  # scaled advisory impact

            # Clip to safety bounds
            delta = max(-MetaMLAdvisor.MAX_DELTA,
                        min(MetaMLAdvisor.MAX_DELTA, delta))

            deltas[sid] = delta

        return MLAdvisoryResult(deltas=deltas)