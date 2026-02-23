from core.regime.activation import (
    AlphaActivationMatrix,
    AlphaActivationRule,
)
from core.regime.taxonomy import MarketRegime


def test_strategy_active_in_allowed_regime():
    matrix = AlphaActivationMatrix(
        rules={
            "trend_alpha": AlphaActivationRule(
                strategy_name="trend_alpha",
                allowed_regimes={
                    MarketRegime.TREND_LOW_VOL,
                    MarketRegime.TREND_HIGH_VOL,
                },
            )
        }
    )

    assert matrix.is_active(
        strategy_name="trend_alpha",
        regime=MarketRegime.TREND_LOW_VOL,
    )


def test_strategy_blocked_in_disallowed_regime():
    matrix = AlphaActivationMatrix(
        rules={
            "mean_reversion": AlphaActivationRule(
                strategy_name="mean_reversion",
                allowed_regimes={
                    MarketRegime.RANGE_LOW_VOL,
                },
            )
        }
    )

    assert not matrix.is_active(
        strategy_name="mean_reversion",
        regime=MarketRegime.TREND_HIGH_VOL,
    )


def test_strategy_not_mapped_defaults_to_off():
    matrix = AlphaActivationMatrix(rules={})

    assert not matrix.is_active(
        strategy_name="unknown_alpha",
        regime=MarketRegime.TREND_LOW_VOL,
    )
