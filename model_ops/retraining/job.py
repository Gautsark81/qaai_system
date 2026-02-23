from dataclasses import dataclass
from typing import List
from .regime import MarketRegime


@dataclass(frozen=True)
class ShadowTrainingJob:
    job_id: str
    model_id: str
    regime: MarketRegime
    lookback_days: int
    model_family: str
    featureset: str
    reasons: List[str]
