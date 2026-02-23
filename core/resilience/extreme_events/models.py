# core/resilience/extreme_events/models.py
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any


class ExtremeEventType(str, Enum):
    NORMAL = "normal"
    MARKET_CRASH = "market_crash"
    LIQUIDITY_FREEZE = "liquidity_freeze"
    VOLATILITY_SPIKE = "volatility_spike"
    SYSTEM_ANOMALY = "system_anomaly"


@dataclass(frozen=True)
class ExtremeEventClassification:
    event_type: ExtremeEventType
    severity: float          # 0.0 → 1.0
    evidence: Dict[str, Any]
