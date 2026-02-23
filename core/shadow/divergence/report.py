from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class DivergenceReport:
    """
    Immutable divergence result.
    """
    has_divergence: bool
    reasons: List[str]

    has_execution_authority: bool = False
    has_capital_authority: bool = False
