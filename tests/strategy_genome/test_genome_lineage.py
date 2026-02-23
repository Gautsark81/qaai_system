import pytest

from modules.strategy_genome.genome import StrategyGenome
from modules.strategy_genome.lineage_store import LineageStore
from modules.strategy_genome.factory import StrategyGenomeFactory


def test_genome_fingerprint_is_deterministic():
    g1 = StrategyGenome(
        strategy_type="mean_reversion",
        symbol_universe="NSE_ALL",
        timeframe="5m",
        parameters={"lookback": 20},
        features={"rsi": True},
        seed=42,
    )

    g2 = StrategyGenome(
        strategy_type="mean_reversion",
        symbol_universe="NSE_ALL",
        timeframe="5m",
        parameters={"lookback": 20},
        features={"rsi": True},
        seed=42,
    )

    assert g1.fingerprint() == g2.fingerprint()


def test_lineage_store_append_only():
    store = LineageStore()
    factory = StrategyGenomeFactory(store)

    root = factory.create_root(
        strategy_type="trend",
        symbol_universe="NSE_ALL",
        timeframe="15m",
        parameters={"ema": 50},
        features={"ema": True},
        seed=1,
    )

    with pytest.raises(ValueError):
        store.add(store.get(root.fingerprint()))


def test_mutation_creates_new_generation():
    store = LineageStore()
    factory = StrategyGenomeFactory(store)

    root = factory.create_root(
        strategy_type="breakout",
        symbol_universe="NSE_ALL",
        timeframe="5m",
        parameters={"range": 10},
        features={"atr": True},
        seed=10,
    )

    child = factory.mutate(
        parent=root,
        new_parameters={"range": 15},
        mutation_reason="optimize_range",
        seed=11,
    )

    assert child.generation == 1
    assert child.parent_id == root.fingerprint()
    assert root.fingerprint() in store.ancestors(child.fingerprint())


def test_lineage_chain_correct():
    store = LineageStore()
    factory = StrategyGenomeFactory(store)

    root = factory.create_root(
        strategy_type="scalping",
        symbol_universe="NSE_ALL",
        timeframe="1m",
        parameters={"spread": 2},
        features={"volume": True},
        seed=5,
    )

    c1 = factory.mutate(
        parent=root,
        new_parameters={"spread": 1},
        mutation_reason="tighten_spread",
        seed=6,
    )

    c2 = factory.mutate(
        parent=c1,
        new_parameters={"spread": 1},
        mutation_reason="confirm_stability",
        seed=7,
    )

    ancestors = store.ancestors(c2.fingerprint())
    assert ancestors == [c1.fingerprint(), root.fingerprint()]
