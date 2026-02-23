# core/strategy_factory/screening/watchlist_models.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class WatchlistEntry:
    strategy_dna: str
    rank: int


@dataclass(frozen=True)
class WatchlistReport:
    entries: Tuple[WatchlistEntry, ...]
    recommended_size: int
    state_hash: str