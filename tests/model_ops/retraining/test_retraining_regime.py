from qaai_system.model_ops.retraining import MarketRegime


def test_market_regime_enum():
    assert MarketRegime.HIGH_VOL.value == "high_vol"
