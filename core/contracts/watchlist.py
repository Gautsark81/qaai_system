# core/contracts/watchlist.py

from dataclasses import dataclass
from typing import List, Dict
from datetime import date


@dataclass(frozen=True)
class WatchlistSymbol:
    symbol: str
    rank: int
    liquidity_score: float
    volatility_score: float
    tags: List[str]


@dataclass(frozen=True)
class WatchlistManifest:
    trading_day: date
    symbols: List[WatchlistSymbol]
    source_screening_version: str
    constraints: Dict[str, float]
    generated_at: str

    def symbol_list(self) -> List[str]:
        return [s.symbol for s in self.symbols]
