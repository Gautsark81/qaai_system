from core.strategy_factory.grammar.operators import arity
import pytest

def test_operator_arity():
    assert arity("add") == 2
    with pytest.raises(ValueError):
        arity("bad")
