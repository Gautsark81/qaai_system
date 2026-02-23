from core.regime.taxonomy import (
    VolatilityRegime,
    TrendRegime,
    MarketRegime,
)


def test_taxonomy_values_are_stable():
    assert VolatilityRegime.LOW.value == "LOW_VOL"
    assert TrendRegime.RANGE.value == "RANGE"
    assert MarketRegime.CHAOTIC.value == "CHAOTIC"
