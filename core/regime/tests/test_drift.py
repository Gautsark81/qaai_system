from core.regime.drift import (
    RegimeDriftDetector,
    RegimeDriftPolicy,
)
from core.regime.taxonomy import MarketRegime


def test_stable_regime():
    detector = RegimeDriftDetector(
        policy=RegimeDriftPolicy(window=5, max_changes=1)
    )

    for _ in range(5):
        detector.update(MarketRegime.TREND_LOW_VOL)

    assert detector.is_stable()
    assert not detector.is_transitioning()


def test_transition_detected():
    detector = RegimeDriftDetector(
        policy=RegimeDriftPolicy(window=5, max_changes=1)
    )

    regimes = [
        MarketRegime.TREND_LOW_VOL,
        MarketRegime.RANGE_LOW_VOL,
        MarketRegime.TREND_LOW_VOL,
        MarketRegime.RANGE_LOW_VOL,
        MarketRegime.TREND_LOW_VOL,
    ]

    for r in regimes:
        detector.update(r)

    assert detector.is_transitioning()
    assert not detector.is_stable()


def test_insufficient_history_not_transition():
    detector = RegimeDriftDetector(
        policy=RegimeDriftPolicy(window=5, max_changes=1)
    )

    detector.update(MarketRegime.TREND_LOW_VOL)
    detector.update(MarketRegime.RANGE_LOW_VOL)

    assert not detector.is_transitioning()


def test_last_regime():
    detector = RegimeDriftDetector(
        policy=RegimeDriftPolicy(window=3, max_changes=1)
    )

    detector.update(MarketRegime.RANGE_LOW_VOL)
    detector.update(MarketRegime.TREND_HIGH_VOL)

    assert detector.last_regime() == MarketRegime.TREND_HIGH_VOL
