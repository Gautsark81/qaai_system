class CapitalScaleRule:
    """
    Computes next capital step.
    """

    @staticmethod
    def next_capital(
        current_capital: float,
        multiplier: float = 1.5,
        max_capital: float | None = None,
    ) -> float:

        next_cap = current_capital * multiplier

        if max_capital is not None:
            return min(next_cap, max_capital)

        return next_cap
