from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from strategies.base import StrategySignal


@dataclass(slots=True)
class RiskDecision:
    approved: bool
    reason: str
    adjusted_size: float
    meta: Dict[str, float] = field(default_factory=dict)


class RiskContextProtocol:
    """
    What risk rules can look at.

    This can be backed by a real portfolio state or a simulated one in tests.
    """

    def total_exposure(self) -> float:
        ...

    def symbol_exposure(self, symbol: str) -> float:
        ...

    def sector_exposure(self, sector: str) -> float:
        ...

    def symbol_volatility(self, symbol: str) -> float:
        ...
