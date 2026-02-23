# core/institution/capital_partition/models.py
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class CapitalEnvelope:
    """
    Hard capital boundary for a portfolio.

    NOTE:
    - No execution authority
    - No leverage math
    """
    portfolio_id: str
    max_capital: float


@dataclass(frozen=True)
class CapitalAllocationView:
    """
    Read-only capital state per portfolio.
    """
    portfolio_id: str
    max_capital: float
    used_capital: float

    @property
    def remaining_capital(self) -> float:
        return max(0.0, self.max_capital - self.used_capital)
