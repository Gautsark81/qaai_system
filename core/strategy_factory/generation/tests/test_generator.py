def test_generator_deterministic():
    from core.strategy_factory.generation.generator import generate_ast

    a1 = generate_ast(1)
    a2 = generate_ast(1)

    assert a1 == a2
