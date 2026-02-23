import inspect

from core.strategy_drift.decay import (
    StrategyHealthHistory,
    StrategyDecayDetector,
)
from core.strategy_drift.drift import (
    StrategyRegimeProfile,
    StrategyRegimeDriftDetector,
)
from core.strategy_drift.drift_signal import StrategyDriftSignal
from core.regime_detection.regime_types import MarketRegime


def test_strategy_decay_detected():
    history = StrategyHealthHistory(scores=[0.9, 0.8, 0.6])

    assert StrategyDecayDetector.has_decay(history) is True


def test_no_decay_when_improving():
    history = StrategyHealthHistory(scores=[0.4, 0.6, 0.8])

    assert StrategyDecayDetector.has_decay(history) is False


def test_regime_mismatch_detected():
    profile = StrategyRegimeProfile(
        preferred_regime=MarketRegime.TRENDING
    )

    mismatch = StrategyRegimeDriftDetector.is_mismatched(
        current_regime=MarketRegime.RANGE_BOUND,
        profile=profile,
    )

    assert mismatch is True


def test_drift_signal_creation():
    signal = StrategyDriftSignal(
        strategy_id="strategy-1",
        signal_type="REGIME_MISMATCH",
        severity="WARNING",
        note="strategy prefers trending markets",
    )

    assert signal.severity == "WARNING"


def test_no_execution_authority():
    modules = [
        StrategyDecayDetector,
        StrategyRegimeDriftDetector,
        StrategyDriftSignal,
    ]

    forbidden = [
        "execute",
        "order",
        "broker",
        "retry",
        "sleep",
        "while",
        "for ",
        "call(",
    ]

    for obj in modules:
        source = inspect.getsource(obj).lower()
        for word in forbidden:
            assert word not in source
