from core.strategy_factory.grammar.primitives import is_valid_primitive

def test_valid_primitives():
    assert is_valid_primitive("price")
    assert not is_valid_primitive("foobar")
