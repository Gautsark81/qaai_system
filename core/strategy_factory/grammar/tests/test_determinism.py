import random
from core.strategy_factory.grammar.ast import ASTNode
from core.strategy_factory.grammar.mutation import mutate

def test_seed_replay():
    random.seed(1)
    a = mutate(ASTNode("price"))
    random.seed(1)
    b = mutate(ASTNode("price"))
    assert a == b
