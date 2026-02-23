from typing import Dict, List
from modules.intelligence.ssr import TradeResult, SSRCalculator
from modules.intelligence.metrics import StrategyMetricsExtractor


class TournamentResultAggregator:
    def __init__(self):
        self.ssr_calc = SSRCalculator()
        self.metrics_extractor = StrategyMetricsExtractor()

    def aggregate(
        self,
        symbol_results: Dict[str, List[TradeResult]],
    ) -> dict:
        """
        Flattens symbol-level trade results into tournament-level metrics.
        """
        all_trades: List[TradeResult] = []

        for trades in symbol_results.values():
            all_trades.extend(trades)

        ssr = self.ssr_calc.compute(all_trades)
        metrics = self.metrics_extractor.extract(all_trades)

        return {
            "ssr": ssr,
            "metrics": metrics,
        }
