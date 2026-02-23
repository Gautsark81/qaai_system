from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CapitalContext:
    """
    Immutable runtime snapshot for capital decisions.

    ❗ Deliberately excludes:
    - strategy_dna
    - requested_capital
    - governance limits

    Those belong to the engine orchestration layer.
    """

    strategy_current_capital: float
    global_capital_used: float
