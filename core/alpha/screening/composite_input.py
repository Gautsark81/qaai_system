# core/alpha/screening/composite_input.py

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CompositeScreeningInput:
    symbol: str
    liquidity: Any
    regime: Any
    statistical_illusion: Any
    cross_factor: Any
    structural_risk: Any
    crowding_risk: Any
    tail_risk: Any
