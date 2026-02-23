from core.strategy_factory.grammar.ast import ASTNode
from core.strategy_factory.grammar.mutation import mutate

def test_mutation_bounded():
    n = ASTNode("price")
    assert mutate(n) == n
