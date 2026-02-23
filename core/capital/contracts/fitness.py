from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class CapitalFitness:
    """
    Immutable capital fitness signal.
    """

    raw_fitness: float
    fragility_penalty: float
    reasons: List[str]
    is_capital_eligible: bool
