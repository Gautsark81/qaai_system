from __future__ import annotations

from dataclasses import dataclass
from typing import List

from core.strategy_factory.health.meta_alpha.cross_strategy_signal import (
    CrossStrategySignal,
)


@dataclass(frozen=True)
class PortfolioRegimeDescriptor:
    """
    Phase 10.2 — Portfolio Regime Descriptor

    Descriptive, advisory-only label representing the
    current portfolio-wide regime.

    MUST NOT:
    - rank strategies
    - select strategies
    - allocate capital
    - gate execution
    """

    name: str
    description: str
    confidence: float
    advisory_only: bool = True

    @classmethod
    def from_signals(
        cls, signals: List[CrossStrategySignal]
    ) -> "PortfolioRegimeDescriptor":
        if not signals:
            return cls(
                name="UNKNOWN",
                description="No signals available",
                confidence=0.0,
            )

        # Extract known signals (by convention, not enforcement)
        mean_health = next(
            (s.value for s in signals if s.name == "HEALTH_MEAN"), None
        )
        dispersion = next(
            (s.value for s in signals if s.name == "HEALTH_DISPERSION"), None
        )

        # Deterministic, see-through heuristic (descriptive only)
        if mean_health is not None and dispersion is not None:
            if mean_health >= 0.6 and dispersion <= 0.15:
                name = "COHERENT"
                desc = "Strategies show aligned health and low dispersion"
            elif dispersion > 0.25:
                name = "FRAGMENTED"
                desc = "Strategies exhibit divergent performance"
            elif mean_health < 0.4:
                name = "UNSTABLE"
                desc = "Overall strategy health is weak"
            else:
                name = "STABLE"
                desc = "Portfolio health is mixed but stable"
        else:
            name = "UNKNOWN"
            desc = "Insufficient signals to determine regime"

        confidence = min((s.confidence for s in signals), default=0.0)

        return cls(
            name=name,
            description=desc,
            confidence=confidence,
        )
