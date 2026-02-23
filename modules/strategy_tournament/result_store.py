from typing import Dict, List
from modules.strategy_tournament.result_schema import StrategyRunResult


class ResultStore:
    """
    Stores raw tournament results.
    """

    def __init__(self):
        self._results: Dict[str, List[StrategyRunResult]] = {}

    def add(self, result: StrategyRunResult) -> None:
        self._results.setdefault(result.strategy_id, []).append(result)

    def get(self, strategy_id: str) -> List[StrategyRunResult]:
        return self._results.get(strategy_id, [])

    def all(self) -> Dict[str, List[StrategyRunResult]]:
        return self._results
