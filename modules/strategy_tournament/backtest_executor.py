# modules/strategy_tournament/backtest_executor.py

from typing import List
from modules.strategy_tournament.dna import StrategyDNA
from modules.strategy_tournament.strategy_adapter import StrategyAdapter
from modules.strategy_tournament.symbol_runner import SymbolRunner
from modules.strategy_tournament.result_store import ResultStore


class BacktestExecutor:
    """
    Executes tournament backtests.
    """

    def __init__(self, symbols: List[str], backtest_engine):
        self.symbols = symbols
        self.runner = SymbolRunner(backtest_engine)
        self.store = ResultStore()

    def run_strategy(self, dna: StrategyDNA) -> None:
        adapter = StrategyAdapter(dna)
        strategy = adapter.build()

        for symbol in self.symbols:
            result = self.runner.run(strategy, symbol)
            self.store.add(result)

    def run_all(self, strategies: List[StrategyDNA]) -> ResultStore:
        for dna in strategies:
            self.run_strategy(dna)
        return self.store
