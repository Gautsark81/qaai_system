from dataclasses import dataclass
from datetime import datetime
from typing import Tuple


@dataclass(frozen=True)
class ViolationPulseResult:
    score: float  # 0–100
    contributors: Tuple[str, ...]
    computed_at: datetime

    @property
    def level(self) -> str:
        if self.score < 10:
            return "CALM"
        if self.score < 30:
            return "WATCH"
        if self.score < 60:
            return "ELEVATED"
        if self.score < 80:
            return "DANGEROUS"
        return "CRITICAL"


def build_violation_pulse(
    *,
    violation_count: int,
    violation_rate: float,
    recent_breaches: Tuple[str, ...],
) -> ViolationPulseResult:
    """
    Phase-1 deterministic violation pulse builder.

    No side effects.
    No I/O.
    No smoothing.
    Pure function.
    """

    # Simple Phase-1 scoring (deterministic, explainable)
    score = min(
        100.0,
        (violation_count * 5.0) + (violation_rate * 50.0)
    )

    return ViolationPulseResult(
        score=round(score, 2),
        contributors=recent_breaches,
        computed_at=datetime.utcnow(),
    )
