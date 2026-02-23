from modules.strategy_genome.lineage_store import LineageStore
from modules.strategy_genome.factory import StrategyGenomeFactory
from modules.strategy_evolution.mutations import MutationOperators, MutationSpec
from modules.strategy_evolution.evolution_engine import EvolutionEngine
from modules.strategy_evolution.diversity import DiversityFilter


def test_evolution_produces_children():
    store = LineageStore()
    factory = StrategyGenomeFactory(store)

    parent = factory.create_root(
        strategy_type="mean_reversion",
        symbol_universe="NSE_ALL",
        timeframe="5m",
        parameters={"lookback": 20, "threshold": 1.5},
        features={"rsi": True},
        seed=1,
    )

    ops = MutationOperators(
        specs=[
            MutationSpec(
                name="lookback_tune",
                reason="tune_lookback",
                max_delta=0.2,
                applies_to=["lookback"],
            ),
            MutationSpec(
                name="threshold_tune",
                reason="tune_threshold",
                max_delta=0.1,
                applies_to=["threshold"],
            ),
        ]
    )

    engine = EvolutionEngine(
        genome_factory=factory,
        mutation_ops=ops,
        max_children_per_parent=2,
    )

    children = engine.evolve(
        parents=[parent],
        seed=42,
    )

    assert len(children) == 2
    assert all(c.parent_id == parent.fingerprint() for c in children)


def test_diversity_filter_removes_duplicates():
    store = LineageStore()
    factory = StrategyGenomeFactory(store)

    parent = factory.create_root(
        strategy_type="trend",
        symbol_universe="NSE_ALL",
        timeframe="15m",
        parameters={"ema": 50},
        features={"ema": True},
        seed=2,
    )

    ops = MutationOperators(
        specs=[
            MutationSpec(
                name="ema_tune",
                reason="tune_ema",
                max_delta=0.0,   # force identical mutation
                applies_to=["ema"],
            )
        ]
    )

    engine = EvolutionEngine(
        genome_factory=factory,
        mutation_ops=ops,
        max_children_per_parent=2,
    )

    children = engine.evolve(
        parents=[parent],
        seed=10,
    )

    filtered = DiversityFilter().filter(children)

    assert len(filtered) == 1
