from core.strategy_factory.fitness.contracts import FitnessInputs


class FragilityEngine:
    """
    Conservative fragility estimator.

    Fragility dominates fitness.
    """

    @staticmethod
    def compute(inputs: FitnessInputs) -> float:
        penalty = 0.0

        # Tail loss dominance (CRITICAL)
        if inputs.tail_loss_ratio > 3.0:
            penalty += 0.4
        elif inputs.tail_loss_ratio > 2.0:
            penalty += 0.25

        # Drawdown sensitivity
        if inputs.max_drawdown > 0.25:
            penalty += 0.3
        elif inputs.max_drawdown > 0.15:
            penalty += 0.15

        # Regime inconsistency
        if inputs.regime_consistency < 0.5:
            penalty += 0.25
        elif inputs.regime_consistency < 0.7:
            penalty += 0.1

        # Low statistical power
        if inputs.trade_count < 30:
            penalty += 0.2
        elif inputs.trade_count < 50:
            penalty += 0.1

        return min(1.0, penalty)
