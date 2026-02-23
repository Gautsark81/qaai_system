from core.regime.health import StrategyHealth
from core.regime.taxonomy import MarketRegime


def test_record_and_ssr_per_regime():
    health = StrategyHealth()

    health.record_outcome(
        regime=MarketRegime.TREND_LOW_VOL,
        success=True,
    )
    health.record_outcome(
        regime=MarketRegime.TREND_LOW_VOL,
        success=False,
    )
    health.record_outcome(
        regime=MarketRegime.TREND_LOW_VOL,
        success=True,
    )

    ssr = health.ssr_for(MarketRegime.TREND_LOW_VOL)
    assert ssr == 2 / 3


def test_ssr_zero_when_no_data():
    health = StrategyHealth()
    assert health.ssr_for(MarketRegime.RANGE_HIGH_VOL) == 0.0


def test_overall_ssr_across_regimes():
    health = StrategyHealth()

    health.record_outcome(
        regime=MarketRegime.TREND_LOW_VOL,
        success=True,
    )
    health.record_outcome(
        regime=MarketRegime.RANGE_LOW_VOL,
        success=False,
    )
    health.record_outcome(
        regime=MarketRegime.RANGE_LOW_VOL,
        success=True,
    )

    assert health.overall_ssr() == 2 / 3
