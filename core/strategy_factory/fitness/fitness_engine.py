from core.strategy_factory.fitness.contracts import (
    FitnessInputs,
    FitnessResult,
)
from core.strategy_factory.fitness.fragility_engine import FragilityEngine


class FitnessEngine:
    @staticmethod
    def compute(inputs: FitnessInputs) -> FitnessResult:
        raw = (
            0.4 * min(inputs.sharpe / 2.0, 1.0)
            + 0.3 * inputs.win_rate
            + 0.3 * inputs.regime_consistency
        )
        raw = max(0.0, min(1.0, raw))

        fragility = FragilityEngine.compute(inputs)
        final = raw - fragility

        return FitnessResult(
            round(raw, 4),
            round(fragility, 4),
            final >= 0.6,
        )
