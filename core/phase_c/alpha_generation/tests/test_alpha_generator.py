from core.strategy_factory.registry import StrategyRegistry
from core.phase_c.alpha_generation.generator import AlphaGenerator
from core.phase_c.alpha_generation.templates import StrategyTemplate


def test_alpha_generator_registers_generated_strategies():
    registry = StrategyRegistry()
    generator = AlphaGenerator(registry)

    template = StrategyTemplate(
        name="mean_revert",
        alpha_stream="rv",
        timeframe="5m",
        base_params={"z": 2.0},
    )

    dnas = generator.generate(
        template=template,
        universe=["NIFTY"],
        param_grid={"z": [1.5, 2.0, 2.5]},
    )

    assert len(dnas) == 3

    for dna in dnas:
        record = registry.get(dna)
        assert record.state == "GENERATED"
