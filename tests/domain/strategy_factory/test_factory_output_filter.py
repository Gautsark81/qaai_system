from domain.strategy_factory.strategy_candidate import StrategyCandidate
from domain.strategy_factory.factory_output_filter import FactoryOutputFilter


def test_only_eligible_strategies_pass():
    c1 = StrategyCandidate("A", None, 0.9, True, None)
    c2 = StrategyCandidate("B", None, 0.6, False, "Low SSR")

    out = FactoryOutputFilter.eligible_only([c1, c2])

    assert len(out) == 1
    assert out[0].strategy_id == "A"
