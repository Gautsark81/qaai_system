from dataclasses import dataclass
from datetime import datetime
from typing import Dict


@dataclass(frozen=True)
class RegimeState:
    timeframe: str
    taxonomy: Dict[str, str]

    confidence: float
    persistence: float
    transition_probability: float

    timestamp: datetime
