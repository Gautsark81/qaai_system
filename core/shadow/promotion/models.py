# core/shadow/promotion/models.py
from dataclasses import dataclass


@dataclass(frozen=True)
class PromotionRehearsalResult:
    strategy_id: str
    eligible: bool
    confidence: float
    reason: str
