from dataclasses import dataclass
from typing import List

from .snapshot import EnsembleSnapshot
from .retirement import RetirementResult
from .replacement import ReplacementQueueResult
from .models import AllocationResult


@dataclass(frozen=True)
class PopulationHealthResult:
    active_count: int
    suspended_count: int
    retirement_candidates: int
    replacement_slots: int
    avg_decay_score: float
    reinforcement_strength: float
    stability_score: float
    snapshot_hash: str


class PopulationHealthEngine:

    @staticmethod
    def evaluate(
        snapshot: EnsembleSnapshot,
        allocation: AllocationResult,
        retirement: RetirementResult,
        replacement: ReplacementQueueResult,
    ) -> PopulationHealthResult:

        total_strategies = len(snapshot.strategies)
        suspended_count = len(allocation.suspensions)
        active_count = total_strategies - suspended_count

        retirement_count = len(retirement.retirement_candidates)
        replacement_count = len(replacement.replacement_slots)

        # Average decay score
        if snapshot.decay_scores:
            avg_decay = sum(snapshot.decay_scores.values()) / len(snapshot.decay_scores)
        else:
            avg_decay = 0.0

        reinforcement_strength = snapshot.reinforcement_strength

        # Deterministic Stability Score (bounded 0–1)
        # High decay + high retirement pressure lowers stability
        decay_component = 1 - avg_decay
        retirement_pressure = 1 - (retirement_count / total_strategies) if total_strategies > 0 else 1.0

        stability_score = max(
            0.0,
            min(1.0, 0.6 * decay_component + 0.4 * retirement_pressure),
        )

        return PopulationHealthResult(
            active_count=active_count,
            suspended_count=suspended_count,
            retirement_candidates=retirement_count,
            replacement_slots=replacement_count,
            avg_decay_score=avg_decay,
            reinforcement_strength=reinforcement_strength,
            stability_score=stability_score,
            snapshot_hash=snapshot.snapshot_hash,
        )