from modules.strategy_population.manager import PopulationManager
from modules.strategy_population.config import PopulationConfig
from modules.strategy_population.fitness_snapshot import FitnessSnapshot
from modules.strategy_genome.lineage_store import LineageStore
from modules.strategy_genome.factory import StrategyGenomeFactory
from modules.strategy_health.state_machine import StrategyState


def test_population_prunes_by_fitness_and_cap():
    store = LineageStore()
    factory = StrategyGenomeFactory(store)

    g1 = factory.create_root(
        strategy_type="trend",
        symbol_universe="NSE_ALL",
        timeframe="5m",
        parameters={"ema": 20},
        features={"ema": True},
        seed=1,
    )

    g2 = factory.mutate(
        parent=g1,
        new_parameters={"ema": 30},
        mutation_reason="tune",
        seed=2,
    )

    fitness = [
        FitnessSnapshot(
            strategy_id=g1.fingerprint(),
            symbol="NIFTY",
            fitness_score=0.9,
            win_rate=0.85,
            max_drawdown=0.03,
            evaluated_at_step=90,
        ),
        FitnessSnapshot(
            strategy_id=g2.fingerprint(),
            symbol="NIFTY",
            fitness_score=0.7,
            win_rate=0.82,
            max_drawdown=0.04,
            evaluated_at_step=95,
        ),
    ]

    states = {
        g1.fingerprint(): StrategyState.ACTIVE,
        g2.fingerprint(): StrategyState.ACTIVE,
    }

    pm = PopulationManager(
        config=PopulationConfig(max_population_per_symbol=1),
        lineage_store=store,
    )

    pop = pm.build_population(
        fitness=fitness,
        states=states,
        current_step=100,
    )

    assert len(pop["NIFTY"]) == 1
    assert pop["NIFTY"][0].strategy_id == g1.fingerprint()


def test_population_blocks_paused_and_old():
    store = LineageStore()
    factory = StrategyGenomeFactory(store)

    g = factory.create_root(
        strategy_type="mean_reversion",
        symbol_universe="NSE_ALL",
        timeframe="5m",
        parameters={"lookback": 10},
        features={"rsi": True},
        seed=3,
    )

    fitness = [
        FitnessSnapshot(
            strategy_id=g.fingerprint(),
            symbol="BANKNIFTY",
            fitness_score=0.8,
            win_rate=0.83,
            max_drawdown=0.02,
            evaluated_at_step=0,
        ),
    ]

    states = {
        g.fingerprint(): StrategyState.PAUSED,
    }

    pm = PopulationManager(
        config=PopulationConfig(max_age_steps=50),
        lineage_store=store,
    )

    pop = pm.build_population(
        fitness=fitness,
        states=states,
        current_step=200,
    )

    assert "BANKNIFTY" not in pop or len(pop["BANKNIFTY"]) == 0
