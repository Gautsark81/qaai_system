from __future__ import annotations

from typing import Dict


class ConcentrationEngine:
    """
    Computes effective concentration using squared weights
    (Herfindahl-style concentration).
    """

    @staticmethod
    def effective_concentration(weights: Dict[str, float]) -> float:
        """
        weights: normalized exposure weights (sum ≈ 1)

        Returns:
            concentration ∈ (0, 1]
            Higher = more concentrated
        """
        return sum(w ** 2 for w in weights.values())
