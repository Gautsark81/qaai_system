# core/alpha/screening/composite_verdict.py

from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass(frozen=True)
class CompositeScreeningVerdict:
    passed: bool
    failed_step: Optional[str]
    blocked_dimensions: Tuple[str, ...]
