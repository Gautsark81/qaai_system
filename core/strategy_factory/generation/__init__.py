# core/strategy_factory/generation/__init__.py

from .population import StrategyPopulation
from .novelty import NoveltyFilter
from .admission import StrategyAdmissionController
from core.strategy_factory.registry import StrategyRegistry


def generate_strategies(seed: int, population_size: int):
    population = StrategyPopulation(seed, population_size)
    novelty = NoveltyFilter()
    registry = StrategyRegistry()
    admission = StrategyAdmissionController(registry)

    asts = population.initialize()
    records = []

    for ast in asts:
        if novelty.is_novel(ast):
            record = admission.admit(ast)
            records.append(record)

    return records
