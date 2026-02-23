from dataclasses import dataclass


@dataclass(frozen=True)
class FitnessSnapshot:
    """
    Normalized fitness output from C1.
    """
    strategy_id: str
    symbol: str
    fitness_score: float       # higher is better
    win_rate: float
    max_drawdown: float
    evaluated_at_step: int
