from modules.strategy_tournament.generator import StrategyGenerator


def test_generator_produces_candidates():
    gen = StrategyGenerator()
    candidates = gen.generate()

    assert len(candidates) > 0
