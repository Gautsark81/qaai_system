import pytest

from core.regime.regime_memory import RegimeMemory
from core.regime.regime_types import MarketRegime


def test_append_adds_event():
    memory = RegimeMemory()

    memory.append(
        symbol="NIFTY",
        regime=MarketRegime.TRENDING,
        confidence=0.9,
        detector_id="detector_a",
        evidence={"vol": "high"},
    )

    assert memory.count() == 1


def test_append_preserves_order():
    memory = RegimeMemory()

    memory.append("NIFTY", MarketRegime.RANGING, 0.6, "d1", {})
    memory.append("NIFTY", MarketRegime.TRENDING, 0.7, "d2", {})

    events = memory.get_history("NIFTY")
    assert events[0].regime == MarketRegime.RANGING
    assert events[1].regime == MarketRegime.TRENDING


def test_append_rejects_invalid_regime():
    memory = RegimeMemory()

    with pytest.raises(ValueError):
        memory.append(
            symbol="NIFTY",
            regime="SIDEWAYS",  # invalid enum
            confidence=0.4,
            detector_id="bad",
            evidence={},
        )
