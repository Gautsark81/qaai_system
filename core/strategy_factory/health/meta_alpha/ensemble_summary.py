from __future__ import annotations

from dataclasses import dataclass
from typing import List

from core.strategy_factory.health.snapshot import StrategyHealthSnapshot


@dataclass(frozen=True)
class EnsembleSummary:
    """
    Descriptive, read-only portfolio-level summary.

    Advisory only.
    """

    count: int
    mean_health: float
    dispersion: float

    @classmethod
    def from_snapshots(
        cls, snapshots: List[StrategyHealthSnapshot]
    ) -> "EnsembleSummary":
        if not snapshots:
            return cls(count=0, mean_health=0.0, dispersion=0.0)

        health_scores = [s.health_score for s in snapshots]

        mean = sum(health_scores) / len(health_scores)
        dispersion = (
            sum((x - mean) ** 2 for x in health_scores) / len(health_scores)
        ) ** 0.5

        return cls(
            count=len(snapshots),
            mean_health=mean,
            dispersion=dispersion,
        )
