from core.regime.confidence import (
    RegimeConfidencePolicy,
    gate_confidence,
)
from core.regime.taxonomy import MarketRegime


def test_confidence_full_in_favorable_regime():
    policy = RegimeConfidencePolicy(
        multipliers={
            MarketRegime.TREND_LOW_VOL: 1.0,
        }
    )

    out = gate_confidence(
        raw_confidence=0.8,
        regime=MarketRegime.TREND_LOW_VOL,
        policy=policy,
    )

    assert out == 0.8


def test_confidence_reduced_in_hostile_regime():
    policy = RegimeConfidencePolicy(
        multipliers={
            MarketRegime.TREND_LOW_VOL: 0.3,
        }
    )

    out = gate_confidence(
        raw_confidence=0.9,
        regime=MarketRegime.TREND_LOW_VOL,
        policy=policy,
    )

    assert out == 0.27


def test_confidence_zero_when_regime_not_defined():
    policy = RegimeConfidencePolicy(multipliers={})

    out = gate_confidence(
        raw_confidence=0.7,
        regime=MarketRegime.CHAOTIC,
        policy=policy,
    )

    assert out == 0.0


def test_confidence_clipped_inputs():
    policy = RegimeConfidencePolicy(
        multipliers={
            MarketRegime.RANGE_LOW_VOL: 2.0,  # clipped
        }
    )

    out = gate_confidence(
        raw_confidence=1.5,
        regime=MarketRegime.RANGE_LOW_VOL,
        policy=policy,
    )

    assert out == 1.0
