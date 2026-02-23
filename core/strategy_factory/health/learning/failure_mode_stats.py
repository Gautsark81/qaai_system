from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from core.strategy_factory.health.death_reason import DeathReason


@dataclass(frozen=True)
class FailureModeStats:
    """
    Immutable statistics describing how strategies fail.

    Contains per-reason counts and normalized ratios.
    """

    total_deaths: int
    reason_counts: Dict[DeathReason, int]
    reason_ratios: Dict[DeathReason, float] = field(init=False)

    def __post_init__(self) -> None:
        if self.total_deaths > 0:
            ratios = {
                reason: count / self.total_deaths
                for reason, count in self.reason_counts.items()
            }
        else:
            ratios = {}

        object.__setattr__(self, "reason_ratios", ratios)

    def __repr__(self) -> str:
        return (
            f"FailureModeStats("
            f"total_deaths={self.total_deaths}, "
            f"reason_counts={dict(self.reason_counts)}, "
            f"reason_ratios={self.reason_ratios}"
            f")"
        )
