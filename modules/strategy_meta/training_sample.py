from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class MetaTrainingSample:
    strategy_id: str
    symbol: str
    regime: str                 # e.g. LOW_VOL, HIGH_VOL, TREND
    features: Dict[str, float]  # context + strategy stats
    label: float                # realized outcome (e.g. expectancy)
