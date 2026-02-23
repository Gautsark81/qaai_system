from dataclasses import dataclass
from typing import Dict, List

from .snapshot import EnsembleSnapshot
from .meta_alpha import MetaAlphaCalculator
from .models import AllocationResult


@dataclass(frozen=True)
class RetirementResult:
    retirement_candidates: List[str]
    snapshot_hash: str


class StrategyRetirementEngine:

    @staticmethod
    def evaluate(
        snapshot: EnsembleSnapshot,
        allocation: AllocationResult,
    ) -> RetirementResult:

        if not snapshot.retirement_enabled:
            return RetirementResult(
                retirement_candidates=[],
                snapshot_hash=snapshot.snapshot_hash,
            )

        meta = MetaAlphaCalculator.calculate(snapshot, allocation)
        avg_score = sum(meta.scores.values()) / len(meta.scores)

        candidates: List[str] = []

        for strategy in snapshot.strategies:

            sid = strategy.strategy_id

            if sid in allocation.suspensions:
                continue

            if strategy.ssr >= snapshot.retirement_min_ssr:
                continue

            decay_score = snapshot.decay_scores.get(sid, 0.0)
            if decay_score <= snapshot.retirement_decay_threshold:
                continue

            meta_score = meta.scores.get(sid, 0.0)
            if meta_score >= avg_score:
                continue

            candidates.append(sid)

        return RetirementResult(
            retirement_candidates=candidates,
            snapshot_hash=snapshot.snapshot_hash,
        )