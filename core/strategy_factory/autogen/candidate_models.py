# core/strategy_factory/autogen/candidate_models.py

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class CandidateStage(str, Enum):
    LAB = "LAB"
    BACKTESTED = "BACKTESTED"
    ROBUST_VALIDATED = "ROBUST_VALIDATED"
    PAPER = "PAPER"
    SHADOW = "SHADOW"
    LIVE_ELIGIBLE = "LIVE_ELIGIBLE"
    LIVE = "LIVE"
    RETIRED = "RETIRED"


@dataclass(frozen=True)
class StrategyCandidate:
    hypothesis_id: str
    hypothesis_hash: str
    stage: CandidateStage
    ssr: Optional[float] = None
    max_drawdown: Optional[float] = None
    shadow_cycles: int = 0