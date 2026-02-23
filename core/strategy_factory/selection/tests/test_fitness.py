from core.strategy_factory.grammar.ast import ASTNode
from core.strategy_factory.grammar.primitives import Primitive
from core.strategy_factory.selection.fitness import evaluate_fitness


def test_fitness_score_bounds():
    ast = ASTNode(Primitive("Momentum", 20))
    fitness = evaluate_fitness(ast)

    assert 0.0 <= fitness.total <= 1.0
