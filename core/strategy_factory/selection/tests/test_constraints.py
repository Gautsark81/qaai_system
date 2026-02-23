import pytest
from core.strategy_factory.grammar.ast import ASTNode
from core.strategy_factory.selection.constraints import assert_selection_constraints


def test_constraint_violation():
    deep = ASTNode("price", children=[ASTNode("price") for _ in range(6)])

    with pytest.raises(ValueError):
        assert_selection_constraints(deep)
