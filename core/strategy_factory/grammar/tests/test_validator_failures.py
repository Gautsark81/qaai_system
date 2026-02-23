import pytest
from core.strategy_factory.grammar.ast import ASTNode
from core.strategy_factory.grammar.validator import validate

def test_invalid_primitive():
    with pytest.raises(ValueError):
        validate(ASTNode("bad"))
