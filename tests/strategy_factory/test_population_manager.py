from qaai_system.strategy_factory.registry import StrategyRegistry
from qaai_system.strategy_factory.generators.population import StrategyPopulation
from qaai_system.strategy_factory.spec import StrategySpec


def test_population_deduplicates():
    reg = StrategyRegistry()
    pop = StrategyPopulation(reg)

    s1 = StrategySpec(entry={"a": 1}, exit={"b": 1})
    s2 = StrategySpec(entry={"a": 1}, exit={"b": 1})

    added = pop.add([s1, s2])

    assert added == 1
    assert len(reg.all()) == 1
