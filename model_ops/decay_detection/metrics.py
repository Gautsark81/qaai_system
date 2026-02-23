from dataclasses import dataclass


@dataclass(frozen=True)
class LiveDecayMetrics:
    sharpe: float
    rolling_sharpe: float
    max_drawdown: float
    volatility: float
    prediction_entropy: float
    psi: float
    shadow_disagreement_rate: float
