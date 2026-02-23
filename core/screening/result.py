from dataclasses import dataclass, field
from typing import List


@dataclass
class ScreeningResult:
    """
    Public screening result object.

    This is the canonical class imported by tests:
        from screening.result import ScreeningResult
    """

    symbol: str
    passed: bool
    score: float
    liquidity: float
    reasons: List[str] = field(default_factory=list)
    rank: int | None = None
