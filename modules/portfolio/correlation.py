from __future__ import annotations

from typing import Dict, List
import math


class CorrelationEngine:
    """
    Computes rolling Pearson correlation between time series.

    Pure, deterministic, replay-safe.
    """

    @staticmethod
    def pearson(x: List[float], y: List[float]) -> float:
        if len(x) != len(y) or len(x) < 2:
            return 0.0

        mean_x = sum(x) / len(x)
        mean_y = sum(y) / len(y)

        num = sum((a - mean_x) * (b - mean_y) for a, b in zip(x, y))
        den_x = sum((a - mean_x) ** 2 for a in x)
        den_y = sum((b - mean_y) ** 2 for b in y)

        den = math.sqrt(den_x * den_y)
        if den == 0:
            return 0.0

        return num / den

    @classmethod
    def correlation_matrix(
        cls,
        series: Dict[str, List[float]],
    ) -> Dict[tuple[str, str], float]:
        keys = list(series.keys())
        matrix: Dict[tuple[str, str], float] = {}

        for i, k1 in enumerate(keys):
            for k2 in keys[i:]:
                corr = cls.pearson(series[k1], series[k2])
                matrix[(k1, k2)] = corr
                matrix[(k2, k1)] = corr

        return matrix
