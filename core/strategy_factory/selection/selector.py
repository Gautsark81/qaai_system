from typing import List
from core.strategy_factory.grammar.ast import ASTNode
from .constraints import assert_selection_constraints
from .scoring import score


class StrategySelector:
    def select(self, population: List[ASTNode], top_k: int) -> List[ASTNode]:
        valid = []

        for ast in population:
            try:
                assert_selection_constraints(ast)
                valid.append(ast)
            except ValueError:
                continue

        ranked = sorted(valid, key=score, reverse=True)
        return ranked[:top_k]
