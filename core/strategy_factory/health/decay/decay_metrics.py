# core/strategy_factory/health/decay/decay_metrics.py

from dataclasses import dataclass


@dataclass(frozen=True)
class DecayMetrics:
    performance: float
    stability: float
    consistency: float
    regime: float

    def composite(self) -> float:
        # Static, auditable weights
        return (
            0.35 * self.performance +
            0.25 * self.stability +
            0.25 * self.consistency +
            0.15 * self.regime
        )
