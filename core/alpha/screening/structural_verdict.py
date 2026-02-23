# core/alpha/screening/structural_verdict.py

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class StructuralRiskVerdict:
    passed: bool
    reasons: Tuple[str, ...]
    blocked_dimensions: Tuple[str, ...]
