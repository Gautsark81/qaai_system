from typing import Dict

from core.capital.correlation_matrix import CorrelationMatrix
from .models import CorrelationWarning


def build_correlation_warnings(
    matrix: CorrelationMatrix,
    threshold: float = 0.9,
) -> Dict[str, CorrelationWarning]:
    """
    Advisory-only correlation governance.

    Governance guarantees:
    - Read-only
    - No execution authority
    - No capital mutation
    """

    correlations = matrix.correlations

    return dict(
        map(
            lambda item: (
                f"{item[0][0]}::{item[0][1]}",
                CorrelationWarning(
                    strategy_a=item[0][0],
                    strategy_b=item[0][1],
                    correlation=item[1],
                    threshold=threshold,
                ),
            ),
            filter(lambda item: item[1] >= threshold, correlations.items()),
        )
    )
