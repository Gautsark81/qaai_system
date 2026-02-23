# core/strategy_reputation/reputation_store.py
from typing import List
from core.strategy_reputation.performance_cycle import PerformanceCycle


class StrategyReputationStore:
    def __init__(self):
        self._cycles: List[PerformanceCycle] = []

    def append(self, cycle: PerformanceCycle) -> None:
        self._cycles.append(cycle)

    def all_cycles(self) -> List[PerformanceCycle]:
        return list(self._cycles)

    def cycles_for_strategy(self, strategy_id: str) -> List[PerformanceCycle]:
        return [c for c in self._cycles if c.strategy_id == strategy_id]
