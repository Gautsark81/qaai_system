from dataclasses import dataclass
from typing import List

from .regime import MarketRegime


@dataclass(frozen=True)
class RetrainingDecision:
    should_retrain: bool
    reasons: List[str]
    regime: MarketRegime
