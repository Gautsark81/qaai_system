# core/shadow/confidence/models.py
from dataclasses import dataclass


@dataclass(frozen=True)
class ShadowConfidenceSnapshot:
    strategy_id: str
    confidence: float          # 0.0 → 1.0
    observations: int
    last_divergence_score: float


@dataclass
class ShadowConfidenceState:
    strategy_id: str
    confidence: float = 0.0
    observations: int = 0
