from dataclasses import dataclass
from typing import List


@dataclass(frozen=True, slots=True)
class ScreeningResult:
    """
    Output of deterministic screening.

    Emitted by: Screening Pipeline
    Consumed by: Watchlist Builder
    """
    symbol: str
    passed: bool
    reasons: List[str]
    score: float
