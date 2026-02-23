from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict


@dataclass(frozen=True)
class DriftSignal:
    metric: str
    baseline: float
    current: float
    delta: float
    severity: str  # LOW | MEDIUM | HIGH


@dataclass(frozen=True)
class AlphaDecayReport:
    strategy_id: str
    half_life_days: float
    decay_rate: float
    status: str  # STABLE | DECAYING | CRITICAL


@dataclass(frozen=True)
class StrategyObservabilitySnapshot:
    strategy_id: str
    alpha_verdict: str
    drift_flags: List[str]
    decay_status: str
    notes: Dict[str, str]
