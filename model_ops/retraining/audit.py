from dataclasses import dataclass
from datetime import datetime
from typing import List

from .regime import MarketRegime


@dataclass(frozen=True)
class RetrainingAuditEvent:
    model_id: str
    regime: MarketRegime
    reasons: List[str]
    timestamp: datetime
