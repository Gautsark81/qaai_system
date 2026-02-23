from __future__ import annotations

from dataclasses import dataclass
from typing import List

from core.strategy_factory.health.snapshot import StrategyHealthSnapshot


@dataclass(frozen=True)
class CrossStrategySignal:
    """
    Phase 10.1 — Cross-Strategy Signal

    Descriptive, advisory-only signal derived from multiple strategies.
    """

    name: str
    description: str
    value: float
    confidence: float
    count: int = 0
    advisory_only: bool = True

    @classmethod
    def from_snapshots(
        cls,
        *,
        name: str,
        snapshots: List[StrategyHealthSnapshot],
    ) -> "CrossStrategySignal":
        if not snapshots:
            return cls(
                name=name,
                description="No strategies available",
                value=0.0,
                confidence=0.0,
                count=0,
            )

        values = [s.health_score for s in snapshots]

        mean_value = sum(values) / len(values)

        return cls(
            name=name,
            description="Mean health across strategies",
            value=mean_value,
            confidence=min(s.confidence for s in snapshots),
            count=len(snapshots),
        )
