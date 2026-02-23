from typing import Dict, List
from modules.intelligence.ssr import TradeResult


class TournamentBacktestRunner:
    def run(
        self,
        strategy,
        symbols: List[str],
    ) -> Dict[str, List[TradeResult]]:
        """
        Returns symbol -> list of TradeResult
        """
        results = {}

        for symbol in symbols:
            results[symbol] = strategy.backtest(symbol)

        return results
