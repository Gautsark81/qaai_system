# core/alpha/screening/tail_risk_verdict.py

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class TailRiskVerdict:
    passed: bool
    reasons: Tuple[str, ...]
    blocked_dimensions: Tuple[str, ...]
