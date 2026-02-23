from qaai_system.strategy_factory.evolution.mutation_engine import MutationEngine
from qaai_system.strategy_factory.spec import StrategySpec


def test_mutation_engine_creates_children():
    parent = StrategySpec(
        family="trend",
        timeframe="5m",
        entry={"indicator": "RSI", "threshold": 55},
        exit={"indicator": "RSI", "threshold": 45},
        lineage={"strategy_id": "root"},
    )

    engine = MutationEngine(seed=42)
    children = engine.mutate([parent])

    assert len(children) == 1
    assert children[0].entry != parent.entry
