# core/watchlist/entry.py

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class WatchlistEntry:
    symbol: str
    screening_passed: bool
    status: str
    suspension_reason: Optional[str] = None
