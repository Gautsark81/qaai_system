# modules/risk/types.py

from dataclasses import dataclass


@dataclass(frozen=True)
class PortfolioSnapshot:
    equity: float
    gross_exposure: float
    positions_by_symbol: dict[str, int]


@dataclass(frozen=True)
class MarketSnapshot:
    atr: float
    volatility: float
