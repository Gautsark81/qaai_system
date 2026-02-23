# core/alpha/screening/crowding_verdict.py

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class CrowdingRiskVerdict:
    passed: bool
    reasons: Tuple[str, ...]
    blocked_dimensions: Tuple[str, ...]
