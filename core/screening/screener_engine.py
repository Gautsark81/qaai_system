# core/screening/screener_engine.py

from datetime import date
from typing import List, Dict
from core.contracts.screening import ScreeningResult, ScreeningSymbol


class ScreenerEngine:
    """
    Deterministic screening engine.
    NO strategy logic.
    NO ML.
    """

    def __init__(
        self,
        min_avg_volume: float,
        min_price: float,
        min_atr: float,
        max_volatility: float,
        screener_version: str = "v1.0",
    ):
        self.min_avg_volume = min_avg_volume
        self.min_price = min_price
        self.min_atr = min_atr
        self.max_volatility = max_volatility
        self.screener_version = screener_version

    def run(self, market_data: Dict[str, Dict]) -> ScreeningResult:
        accepted: List[ScreeningSymbol] = []
        rejected: Dict[str, str] = {}

        for symbol, metrics in market_data.items():
            if metrics["avg_volume"] < self.min_avg_volume:
                rejected[symbol] = "Low liquidity"
                continue
            if metrics["price"] < self.min_price:
                rejected[symbol] = "Low price"
                continue
            if metrics["atr"] < self.min_atr:
                rejected[symbol] = "Low ATR"
                continue
            if metrics["volatility"] > self.max_volatility:
                rejected[symbol] = "Excess volatility"
                continue

            accepted.append(
                ScreeningSymbol(
                    symbol=symbol,
                    avg_volume=metrics["avg_volume"],
                    atr=metrics["atr"],
                    volatility=metrics["volatility"],
                    price=metrics["price"],
                    reason="Passed screening",
                )
            )

        return ScreeningResult(
            trading_day=date.today(),
            universe="NSE_EQ",
            symbols=accepted,
            rejected=rejected,
            screener_version=self.screener_version,
        )
