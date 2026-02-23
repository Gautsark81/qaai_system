from core.strategy_factory.registry import StrategyRegistry
from core.strategy_intake.intake import StrategyIntake


def test_strategy_intake_registers_and_returns_dna():
    registry = StrategyRegistry()
    intake = StrategyIntake(registry)

    dna = intake.submit(
        name="trend_v1",
        alpha_stream="trend",
        timeframe="5m",
        universe=["NIFTY"],
        params={"len": 50},
    )

    record = registry.get(dna)
    assert record.spec.name == "trend_v1"
    assert record.state == "GENERATED"
