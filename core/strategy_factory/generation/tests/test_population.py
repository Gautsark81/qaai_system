def test_population_size():
    from core.strategy_factory.generation.population import StrategyPopulation

    pop = StrategyPopulation(seed=1, size=5)
    asts = pop.initialize()

    assert len(asts) == 5
