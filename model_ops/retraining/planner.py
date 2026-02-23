from dataclasses import dataclass
from typing import List

from .regime import MarketRegime


@dataclass(frozen=True)
class RetrainingPlan:
    regime: MarketRegime
    lookback_days: int
    model_family: str
    featureset: str
    reasons: List[str]
