# core/capital/correlation_matrix.py

from typing import Dict, Tuple


class CorrelationMatrix:
    """
    Stores pairwise correlations.
    """

    def __init__(self, correlations: Dict[Tuple[str, str], float]):
        self.correlations = correlations

    def get(self, a: str, b: str) -> float:
        if a == b:
            return 1.0
        return self.correlations.get((a, b), 0.0)

    @classmethod
    def from_pairs(cls, *pairs):
        """
        Deterministic helper for constructing a correlation matrix
        from (strategy_a, strategy_b, correlation) tuples.

        Governance guarantees:
        - Read-only
        - No execution authority
        - No capital mutation
        """
        correlations = dict(
            map(
                lambda p: ((p[0], p[1]), float(p[2])),
                pairs,
            )
        )
        return cls(correlations)