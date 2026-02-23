# core/strategy_factory/generation/population.py
from typing import List
from core.strategy_factory.grammar.ast import ASTNode
from .generator import generate_ast
from .mutation_policy import mutate_ast

class StrategyPopulation:
    def __init__(self, seed: int, size: int):
        self.seed = seed
        self.size = size

    def initialize(self) -> List[ASTNode]:
        return [generate_ast(self.seed + i) for i in range(self.size)]

    def evolve(self, previous: List[ASTNode]) -> List[ASTNode]:
        return [
            mutate_ast(ast, self.seed + i)
            for i, ast in enumerate(previous)
        ]
