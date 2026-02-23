# core/strategy_factory/screening/screening_models.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple
from decimal import Decimal


@dataclass(frozen=True)
class ScreeningScore:
    """
    Deterministic screening score.

    No authority.
    Pure evaluation signal.
    """

    strategy_dna: str
    score: Decimal
    rank: int
    metrics_hash: str


@dataclass(frozen=True)
class ScreeningResult:
    """
    Immutable screening result container.

    - Sorted by rank
    - Deterministic
    - Replay-safe
    """

    scores: Tuple[ScreeningScore, ...]
    state_hash: str