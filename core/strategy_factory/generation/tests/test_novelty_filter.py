def test_novelty_filter():
    from core.strategy_factory.generation.generator import generate_ast
    from core.strategy_factory.generation.novelty import NoveltyFilter

    nf = NoveltyFilter()
    ast = generate_ast(1)

    assert nf.is_novel(ast)
    assert not nf.is_novel(ast)
