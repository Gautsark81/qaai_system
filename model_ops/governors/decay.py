class CapitalDecayPolicy:
    """
    Defines how capital is reduced once rollback is triggered.
    """

    def next_weight(self, current_weight: float) -> float:
        raise NotImplementedError


class HardKillDecay(CapitalDecayPolicy):
    """
    Immediate kill-switch.
    """

    def next_weight(self, current_weight: float) -> float:
        return 0.0


class LinearDecay(CapitalDecayPolicy):
    """
    Gradual capital reduction with deterministic rounding.
    """

    def __init__(self, step: float, precision: int = 6):
        if step <= 0.0:
            raise ValueError("Decay step must be positive")
        self.step = step
        self.precision = precision

    def next_weight(self, current_weight: float) -> float:
        next_value = current_weight - self.step
        next_value = max(0.0, next_value)

        # Deterministic rounding for audit safety
        return round(next_value, self.precision)
