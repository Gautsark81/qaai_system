import pytest
from datetime import datetime, timezone

from core.regime.regime_event import RegimeEvent
from core.regime.regime_types import MarketRegime


def test_regime_event_is_immutable():
    event = RegimeEvent(
        symbol="NIFTY",
        regime=MarketRegime.TRENDING,
        confidence=0.82,
        detector_id="volatility_detector",
        evidence={"atr": 1.2},
    )

    with pytest.raises(Exception):
        event.confidence = 0.5


def test_regime_event_has_timezone_aware_timestamp():
    event = RegimeEvent(
        symbol="BANKNIFTY",
        regime=MarketRegime.RANGING,
        confidence=0.55,
        detector_id="range_detector",
        evidence={},
    )

    assert isinstance(event.timestamp, datetime)
    assert event.timestamp.tzinfo is not None
    assert event.timestamp.tzinfo.utcoffset(event.timestamp) is not None


def test_regime_event_requires_valid_confidence_bounds():
    with pytest.raises(ValueError):
        RegimeEvent(
            symbol="NIFTY",
            regime=MarketRegime.TRENDING,
            confidence=1.5,
            detector_id="bad_detector",
            evidence={},
        )
