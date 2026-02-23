from core.regime.regime_memory import RegimeMemory
from core.regime.regime_types import MarketRegime


def test_get_latest_returns_most_recent():
    memory = RegimeMemory()

    memory.append("NIFTY", MarketRegime.RANGING, 0.4, "d1", {})
    memory.append("NIFTY", MarketRegime.TRENDING, 0.8, "d2", {})

    latest = memory.get_latest("NIFTY")
    assert latest.regime == MarketRegime.TRENDING


def test_get_history_with_window():
    memory = RegimeMemory()

    for _ in range(5):
        memory.append("NIFTY", MarketRegime.RANGING, 0.5, "d", {})

    history = memory.get_history("NIFTY", window=3)
    assert len(history) == 3


def test_regime_duration_computation():
    memory = RegimeMemory()

    memory.append("NIFTY", MarketRegime.RANGING, 0.5, "d1", {})
    memory.append("NIFTY", MarketRegime.TRENDING, 0.7, "d2", {})

    durations = memory.get_regime_durations("NIFTY")

    assert MarketRegime.RANGING in durations
    assert durations[MarketRegime.RANGING] >= 0
