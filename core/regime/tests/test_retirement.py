from core.regime.retirement import (
    AlphaRetirementEngine,
    AlphaRetirementPolicy,
)
from core.regime.taxonomy import MarketRegime


def test_alpha_not_retired_when_ssr_healthy():
    engine = AlphaRetirementEngine(
        AlphaRetirementPolicy(min_ssr=0.4, max_consecutive_failures=3)
    )

    for _ in range(5):
        engine.update(
            alpha_id="alpha_1",
            regime=MarketRegime.TREND_LOW_VOL,
            regime_ssr=0.6,
        )

    assert not engine.should_retire("alpha_1")
    assert engine.failure_count("alpha_1") == 0


def test_alpha_soft_retirement_after_consecutive_failures():
    engine = AlphaRetirementEngine(
        AlphaRetirementPolicy(min_ssr=0.5, max_consecutive_failures=3)
    )

    for _ in range(3):
        engine.update(
            alpha_id="alpha_2",
            regime=MarketRegime.RANGE_HIGH_VOL,
            regime_ssr=0.3,
        )

    assert engine.should_retire("alpha_2")
    assert engine.failure_count("alpha_2") == 3


def test_recovery_resets_failure_counter():
    engine = AlphaRetirementEngine(
        AlphaRetirementPolicy(min_ssr=0.5, max_consecutive_failures=3)
    )

    engine.update(
        alpha_id="alpha_3",
        regime=MarketRegime.TREND_LOW_VOL,
        regime_ssr=0.2,
    )

    engine.update(
        alpha_id="alpha_3",
        regime=MarketRegime.TREND_LOW_VOL,
        regime_ssr=0.7,
    )

    assert not engine.should_retire("alpha_3")
    assert engine.failure_count("alpha_3") == 0
