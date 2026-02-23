import inspect

from core.regime_detection.features import RegimeFeatures
from core.regime_detection.classifier import RegimeClassifier
from core.regime_detection.regime_types import MarketRegime
from core.regime_detection.regime_snapshot import RegimeSnapshot


def test_trending_regime():
    features = RegimeFeatures(
        volatility=0.3,
        trend_strength=0.9,
        range_ratio=0.2,
    )

    regime = RegimeClassifier.classify(features)
    assert regime == MarketRegime.TRENDING


def test_volatile_regime():
    features = RegimeFeatures(
        volatility=0.9,
        trend_strength=0.1,
        range_ratio=0.4,
    )

    regime = RegimeClassifier.classify(features)
    assert regime == MarketRegime.VOLATILE


def test_regime_snapshot_creation():
    snapshot = RegimeSnapshot(
        timestamp=1000,
        regime=MarketRegime.RANGE_BOUND,
        confidence=0.8,
    )

    assert snapshot.regime == MarketRegime.RANGE_BOUND
    assert snapshot.confidence == 0.8


def test_no_execution_authority():
    modules = [
        RegimeClassifier,
        RegimeSnapshot,
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
