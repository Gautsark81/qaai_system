from typing import Dict, List
import math

from modules.strategy_allocation.contracts import (
    AllocationCandidate,
    AllocationResult,
)
from modules.strategy_allocation.config import AllocationConfig


class CapitalAllocator:
    """
    Deterministic, risk-first capital allocator.

    Produces normalized weights per symbol.
    """

    def __init__(self, *, config: AllocationConfig):
        self.config = config

    # --------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------

    def allocate(
        self,
        *,
        candidates: List[AllocationCandidate],
    ) -> AllocationResult:

        scores: Dict[str, float] = {}
        reasons: Dict[str, List[str]] = {}

        # -------------------------
        # Eligibility filtering
        # -------------------------
        eligible = []
        for c in candidates:
            r = []

            if c.health_score < self.config.min_health:
                r.append("Health below threshold")
            if c.max_drawdown > self.config.max_drawdown:
                r.append("Drawdown above cap")

            if r:
                reasons[c.strategy_id] = r
                continue

            eligible.append(c)

        if not eligible:
            return AllocationResult(weights={}, reasons=reasons)

        # -------------------------
        # Scoring
        # -------------------------
        for c in eligible:
            longevity_score = self._longevity_score(c.age_steps)

            score = (
                self.config.health_weight * c.health_score
                + self.config.fitness_weight * c.fitness_score
                + self.config.longevity_weight * longevity_score
            )

            scores[c.strategy_id] = max(score, 0.0)
            reasons[c.strategy_id] = [
                f"health={round(c.health_score,3)}",
                f"fitness={round(c.fitness_score,3)}",
                f"longevity={round(longevity_score,3)}",
            ]

        # -------------------------
        # Normalization
        # -------------------------
        total = sum(scores.values())
        if total <= 0:
            return AllocationResult(weights={}, reasons=reasons)

        weights = {
            sid: round(score / total, 6)
            for sid, score in scores.items()
        }

        # Final normalization guard
        norm = sum(weights.values())
        if norm > 0:
            weights = {k: v / norm for k, v in weights.items()}

        return AllocationResult(weights=weights, reasons=reasons)

    # --------------------------------------------------
    # INTERNALS
    # --------------------------------------------------

    def _longevity_score(self, age_steps: int) -> float:
        """
        Smoothly increases with age, saturating at 1.0.
        """
        hl = self.config.longevity_half_life
        return 1.0 - math.exp(-age_steps / max(hl, 1))
