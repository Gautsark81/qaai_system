# core/strategy_factory/health/decay/decay_report.py

from dataclasses import dataclass
from datetime import datetime
from .decay_state import AlphaDecayState
from .decay_metrics import DecayMetrics


@dataclass(frozen=True)
class AlphaDecayReport:
    strategy_id: str
    metrics: DecayMetrics
    score: float
    state: AlphaDecayState
    confidence: float
    evaluated_at: datetime
