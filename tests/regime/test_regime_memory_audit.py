import pytest

from core.regime.regime_memory import RegimeMemory
from core.regime.regime_types import MarketRegime


def test_memory_is_append_only():
    memory = RegimeMemory()

    memory.append("NIFTY", MarketRegime.TRENDING, 0.9, "d", {})

    with pytest.raises(AttributeError):
        memory._events = []  # internal mutation forbidden


def test_returned_events_are_read_only():
    memory = RegimeMemory()
    memory.append("NIFTY", MarketRegime.RANGING, 0.6, "d", {})

    event = memory.get_latest("NIFTY")

    with pytest.raises(Exception):
        event.regime = MarketRegime.TRENDING
