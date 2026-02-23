from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class EvolutionVelocityResult:
    retirement_rate: float
    activation_rate: float
    avg_decay_trend: float
    stability_trend: float


class EvolutionVelocityEngine:

    @staticmethod
    def evaluate(
        retirement_history: List[int],
        activation_history: List[int],
        decay_history: List[float],
        stability_history: List[float],
    ) -> EvolutionVelocityResult:

        def rate(series):
            if len(series) < 2:
                return 0.0
            return (series[-1] - series[0]) / max(1, len(series) - 1)

        retirement_rate = rate(retirement_history)
        activation_rate = rate(activation_history)
        avg_decay_trend = rate(decay_history)
        stability_trend = rate(stability_history)

        return EvolutionVelocityResult(
            retirement_rate=retirement_rate,
            activation_rate=activation_rate,
            avg_decay_trend=avg_decay_trend,
            stability_trend=stability_trend,
        )