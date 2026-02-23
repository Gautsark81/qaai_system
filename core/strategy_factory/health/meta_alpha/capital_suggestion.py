from __future__ import annotations

from dataclasses import dataclass
from typing import List

from core.strategy_factory.health.meta_alpha.cross_strategy_signal import (
    CrossStrategySignal,
)
from core.strategy_factory.health.meta_alpha.portfolio_regime import (
    PortfolioRegimeDescriptor,
)


@dataclass(frozen=True)
class CapitalSuggestion:
    """
    Phase 10.3 — Capital Suggestion

    Advisory-only, non-binding capital posture suggestion.
    This object MUST NEVER:
    - allocate capital
    - enforce limits
    - override risk
    - trigger execution
    - influence lifecycle transitions
    """

    name: str
    message: str
    confidence: float
    advisory_only: bool = True

    @classmethod
    def from_context(
        cls,
        *,
        regime: PortfolioRegimeDescriptor,
        signals: List[CrossStrategySignal],
    ) -> "CapitalSuggestion":
        """
        Derive a descriptive capital bias suggestion from
        portfolio regime + cross-strategy signals.

        Deterministic and advisory only.
        """

        # Default posture
        name = "NEUTRAL"
        message = "No strong capital bias detected"
        confidence = regime.confidence

        # Simple, transparent heuristics (descriptive only)
        mean_health = next(
            (s.value for s in signals if s.name == "HEALTH_MEAN"), None
        )

        if regime.name == "COHERENT" and mean_health is not None:
            if mean_health >= 0.6:
                name = "RISK_ON"
                message = (
                    "Portfolio regime coherent with improving strategy breadth"
                )
        elif regime.name in {"FRAGMENTED", "UNSTABLE"}:
            name = "RISK_OFF"
            message = (
                "Portfolio signals suggest caution due to divergent performance"
            )

        return cls(
            name=name,
            message=message,
            confidence=confidence,
        )
