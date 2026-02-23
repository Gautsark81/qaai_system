from dataclasses import dataclass


@dataclass(frozen=True)
class StrategyHealthScore:
    """
    Advisory health score for a strategy.

    Score range: 0.0 (worst) to 1.0 (best)
    """

    score: float
    status: str
