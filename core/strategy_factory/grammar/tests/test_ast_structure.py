from core.strategy_factory.grammar.ast import ASTNode

def test_depth_and_count():
    n = ASTNode("price")
    assert n.depth() == 1
    assert n.node_count() == 1
