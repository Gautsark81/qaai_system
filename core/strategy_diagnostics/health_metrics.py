from dataclasses import dataclass


@dataclass(frozen=True)
class StrategyHealthMetrics:
    """
    Immutable performance metrics snapshot.

    All values must be precomputed upstream.
    """

    pnl: float
    drawdown: float
    win_rate: float
