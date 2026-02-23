from core.resilience.extreme_events.classifier import ExtremeEventClassifier
from core.resilience.extreme_events.models import ExtremeEventType


def test_normal_conditions():
    classifier = ExtremeEventClassifier()
    result = classifier.classify(metrics={"market_return": 0.01})

    assert result.event_type == ExtremeEventType.NORMAL
    assert result.severity == 0.0


def test_market_crash_detected():
    classifier = ExtremeEventClassifier()
    result = classifier.classify(metrics={"market_return": -0.1})

    assert result.event_type == ExtremeEventType.MARKET_CRASH
    assert result.severity > 0.0


def test_liquidity_freeze_detected():
    classifier = ExtremeEventClassifier()
    result = classifier.classify(metrics={"liquidity": 0.1})

    assert result.event_type == ExtremeEventType.LIQUIDITY_FREEZE
    assert result.severity > 0.5


def test_volatility_spike_detected():
    classifier = ExtremeEventClassifier()
    result = classifier.classify(metrics={"volatility": 0.8})

    assert result.event_type == ExtremeEventType.VOLATILITY_SPIKE


def test_system_anomaly_takes_priority():
    classifier = ExtremeEventClassifier()
    result = classifier.classify(
        metrics={
            "system_error_rate": 0.4,
            "market_return": -0.2,
            "volatility": 1.0,
        }
    )

    assert result.event_type == ExtremeEventType.SYSTEM_ANOMALY
