from core.strategy_factory.grammar.ast import ASTNode
from core.strategy_factory.selection.scoring import score


def test_score_returns_float():
    ast = ASTNode("price")
    assert isinstance(score(ast), float)
