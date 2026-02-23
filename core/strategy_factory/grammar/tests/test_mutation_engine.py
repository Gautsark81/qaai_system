from core.strategy_factory.grammar.primitives import Primitive
from core.strategy_factory.grammar.ast import ASTNode
from core.strategy_factory.grammar.mutation import mutate_window


def test_mutation_changes_window():
    ast = ASTNode(Primitive("Momentum", 20))
    mutated = mutate_window(ast)

    assert mutated.node.window != 20
