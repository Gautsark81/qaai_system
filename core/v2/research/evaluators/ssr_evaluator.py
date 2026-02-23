from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class SSREvaluation:
    total: int
    successes: int
    ssr: float


class SSREvaluator:
    """
    Computes Shadow Strategy Success Ratio (SSR).

    Expects an iterable of booleans indicating success/failure.
    """

    def evaluate(self, outcomes: Iterable[bool]) -> SSREvaluation:
        outcomes = list(outcomes)

        total = len(outcomes)
        if total == 0:
            return SSREvaluation(total=0, successes=0, ssr=0.0)

        successes = sum(1 for o in outcomes if o)
        ssr = successes / total

        return SSREvaluation(
            total=total,
            successes=successes,
            ssr=ssr,
        )
