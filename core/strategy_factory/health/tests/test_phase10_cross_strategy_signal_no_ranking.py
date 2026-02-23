from core.strategy_factory.health.meta_alpha.cross_strategy_signal import (
    CrossStrategySignal,
)


def test_cross_strategy_signal_has_no_ranking_or_weighting():
    forbidden = [
        "rank",
        "weight",
        "select",
        "optimize",
        "allocate",
        "vote",
    ]

    for attr in forbidden:
        assert not hasattr(CrossStrategySignal, attr)
