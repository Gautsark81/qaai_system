from dataclasses import dataclass

from core.live_ops.enums import StrategyStage, PromotionDecision


@dataclass(frozen=True, slots=True)
class PromotionRequest:
    """
    Promotion governance decision.

    Emitted by: Promotion Engine
    Consumed by: Operator / Dashboard
    """
    strategy_id: str
    from_stage: StrategyStage
    to_stage: StrategyStage
    decision: PromotionDecision
    reason: str
