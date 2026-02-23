# core/dashboard/nulls.py

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class EmptyScreeningSnapshot:
    """
    Represents absence of screening context.
    Explicitly empty, immutable, deterministic.
    """
    passed: bool = False
    blocked_dimensions: Tuple[str, ...] = ()
    failed_step: str | None = None


@dataclass(frozen=True)
class EmptyCapitalSnapshot:
    """
    Represents absence of capital context.
    Observational only.
    """
    total_capital: float = 0.0
    allocated_capital: float = 0.0
    free_capital: float = 0.0
