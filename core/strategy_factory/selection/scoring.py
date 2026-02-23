from core.strategy_factory.grammar.ast import ASTNode
from .fitness import evaluate_fitness


def score(ast: ASTNode) -> float:
    fitness = evaluate_fitness(ast)
    return fitness.total
