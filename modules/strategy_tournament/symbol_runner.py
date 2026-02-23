# modules/strategy_tournament/symbol_runner.py

from modules.strategy_tournament.result_schema import StrategyRunResult


class SymbolRunner:
    """
    Runs a single strategy on a single symbol using
    the existing backtest engine.
    """

    def __init__(self, backtest_engine):
        self.engine = backtest_engine

    def run(self, strategy, symbol: str) -> StrategyRunResult:
        """
        Execute backtest and return raw results.
        Assumes engine exposes run(strategy, symbol).
        """

        report = self.engine.run(strategy=strategy, symbol=symbol)

        return StrategyRunResult(
            strategy_id=strategy.strategy_id,
            symbol=symbol,
            trades=report.trades,
            total_pnl=report.total_pnl,
            max_drawdown=report.max_drawdown,
            trade_count=len(report.trades),
        )
