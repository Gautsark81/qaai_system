from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class CapitalUsageEvent:
    """
    Immutable capital usage record.

    Represents a single capital allocation attempt.
    """

    strategy_dna: str
    requested_capital: float
    approved_capital: float
    deployed_capital: float
    created_at: datetime
    pnl_realized: Optional[float] = None