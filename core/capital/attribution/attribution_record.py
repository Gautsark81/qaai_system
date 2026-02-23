from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class CapitalAttributionRecord:
    """
    Immutable explanation of a capital allocation decision.
    """
    dna: str
    final_weight: float
    ssr: float
    confidence: float
    regime_score: float
    raw_score: float
