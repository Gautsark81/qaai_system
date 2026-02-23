# core/contracts/screening.py

from dataclasses import dataclass
from typing import List, Dict
from datetime import date


@dataclass(frozen=True)
class ScreeningSymbol:
    symbol: str
    avg_volume: float
    atr: float
    volatility: float
    price: float
    reason: str


@dataclass(frozen=True)
class ScreeningResult:
    trading_day: date
    universe: str
    symbols: List[ScreeningSymbol]
    rejected: Dict[str, str]  # symbol -> rejection reason
    screener_version: str

    def symbol_list(self) -> List[str]:
        return [s.symbol for s in self.symbols]
