def test_strategy_generation_count():
    from core.v2.orchestration.strategy_generation import StrategyGenerator

    gen = StrategyGenerator()
    candidates = gen.generate(5)

    assert len(candidates) == 5
    assert all(c.strategy_id for c in candidates)
