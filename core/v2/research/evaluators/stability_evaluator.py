from __future__ import annotations

import statistics
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class StabilityEvaluation:
    count: int
    mean: float
    variance: float
    stddev: float


class StabilityEvaluator:
    """
    Measures robustness and consistency of numeric outcomes.
    """

    def evaluate(self, values: Iterable[float]) -> StabilityEvaluation:
        values = list(values)
        n = len(values)

        if n == 0:
            return StabilityEvaluation(
                count=0,
                mean=0.0,
                variance=0.0,
                stddev=0.0,
            )

        if n == 1:
            return StabilityEvaluation(
                count=1,
                mean=values[0],
                variance=0.0,
                stddev=0.0,
            )

        mean = statistics.mean(values)
        variance = statistics.variance(values)
        stddev = statistics.stdev(values)

        return StabilityEvaluation(
            count=n,
            mean=mean,
            variance=variance,
            stddev=stddev,
        )
