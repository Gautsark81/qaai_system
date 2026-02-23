from core.strategy_factory.health.meta_alpha.cross_strategy_signal import (
    CrossStrategySignal,
)


def test_cross_strategy_signals_have_no_authority():
    forbidden = [
        "execute",
        "allocate_capital",
        "promote",
        "demote",
        "override_risk",
        "gate",
    ]

    for attr in forbidden:
        assert not hasattr(CrossStrategySignal, attr)
