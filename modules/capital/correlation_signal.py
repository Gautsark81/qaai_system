from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from modules.portfolio.correlation import CorrelationEngine
from modules.portfolio.concentration import ConcentrationEngine


@dataclass(frozen=True)
class CorrelationSignal:
    """
    Advisory signal to penalize correlated exposure.
    """

    correlation_threshold: float = 0.75
    min_scale: float = 0.60

    def scale_from_series(
        self,
        *,
        series: Dict[str, list[float]],
        weights: Dict[str, float],
    ) -> tuple[float, str]:

        corr_matrix = CorrelationEngine.correlation_matrix(series)

        # Count highly correlated pairs
        high_corr_pairs = [
            (a, b)
            for (a, b), c in corr_matrix.items()
            if a != b and abs(c) >= self.correlation_threshold
        ]

        concentration = ConcentrationEngine.effective_concentration(weights)

        if not high_corr_pairs:
            return 1.0, "No high correlation"

        # Penalize proportionally to concentration
        scale = max(self.min_scale, 1.0 - concentration)

        reason = (
            f"HighCorrPairs={len(high_corr_pairs)} "
            f"Concentration={concentration:.2f}"
        )

        return scale, reason
