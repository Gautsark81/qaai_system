from dataclasses import dataclass

from core.live_ops.enums import StrategyStage


@dataclass(frozen=True, slots=True)
class StrategyCandidate:
    """
    Strategy candidate contract.

    Emitted by: Strategy Factory
    Consumed by: Tournament / Promotion
    """
    strategy_id: str
    stage: StrategyStage
    ssr: float
    sharpe: float
    max_drawdown: float
