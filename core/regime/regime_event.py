# core/regime/regime_event.py

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any

from core.regime.regime_types import MarketRegime


@dataclass(frozen=True)
class RegimeEvent:
    symbol: str
    regime: MarketRegime
    confidence: float
    detector_id: str
    evidence: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not isinstance(self.regime, MarketRegime):
            raise ValueError("Invalid regime type")

        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("Confidence must be between 0 and 1")

        if self.timestamp.tzinfo is None or self.timestamp.tzinfo.utcoffset(self.timestamp) is None:
            raise ValueError("Timestamp must be timezone-aware")
