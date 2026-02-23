def test_mutation_safe():
    from core.strategy_factory.generation.generator import generate_ast
    from core.strategy_factory.generation.mutation_policy import mutate_ast

    ast = generate_ast(1)
    mutated = mutate_ast(ast, 2)

    assert ast != mutated
