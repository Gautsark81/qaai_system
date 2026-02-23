# core/alpha/screening/tail_risk_evidence.py

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class TailRiskEvidence:
    symbol: str
    crisis_regime_flags: Tuple[str, ...]
    volatility_explosion_flags: Tuple[str, ...]
    gap_risk_flags: Tuple[str, ...]
    correlation_breakdown_flags: Tuple[str, ...]
    convexity_failure_flags: Tuple[str, ...]
