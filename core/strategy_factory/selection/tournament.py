from typing import List
from core.strategy_factory.grammar.ast import ASTNode
from .selector import StrategySelector


class StrategyTournament:
    def __init__(self, rounds: int = 1):
        self.rounds = rounds
        self.selector = StrategySelector()

    def run(self, population: List[ASTNode], survivors: int) -> List[ASTNode]:
        current = population

        for _ in range(self.rounds):
            current = self.selector.select(current, survivors)

        return current
