from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime, timezone


@dataclass(frozen=True)
class SignalCandidate:
    symbol: str
    rank: int
    confidence: float
    source: str
    features: Dict[str, float]
    reasons: List[str]


@dataclass(frozen=True)
class StrategyIntakeBatch:
    generated_at: datetime
    candidates: List[SignalCandidate]
    constraints: Dict[str, object]
