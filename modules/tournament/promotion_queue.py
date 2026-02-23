from dataclasses import dataclass


@dataclass(frozen=True)
class PromotionRequest:
    strategy_id: str
    stage: str  # "PAPER" → "LIVE_CANDIDATE"
    reason: str
