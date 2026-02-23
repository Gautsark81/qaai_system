import time

from core.regime.regime_memory import RegimeMemory
from core.regime.regime_types import MarketRegime
from core.regime.regime_stability import RegimeStability


def _append_with_sleep(memory, symbol, regime, confidence, sleep_s=0.01):
    memory.append(
        symbol=symbol,
        regime=regime,
        confidence=confidence,
        detector_id="test_detector",
        evidence={},
    )
    time.sleep(sleep_s)


def test_switch_count():
    memory = RegimeMemory()

    _append_with_sleep(memory, "NIFTY", MarketRegime.RANGING, 0.6)
    _append_with_sleep(memory, "NIFTY", MarketRegime.TRENDING, 0.7)
    _append_with_sleep(memory, "NIFTY", MarketRegime.RANGING, 0.5)

    stability = RegimeStability(memory)

    assert stability.switch_count("NIFTY") == 2


def test_average_regime_duration_positive():
    memory = RegimeMemory()

    _append_with_sleep(memory, "NIFTY", MarketRegime.RANGING, 0.6)
    _append_with_sleep(memory, "NIFTY", MarketRegime.TRENDING, 0.7)

    stability = RegimeStability(memory)

    avg_duration = stability.average_regime_duration("NIFTY")
    assert avg_duration > 0.0


def test_stability_score_bounds():
    memory = RegimeMemory()

    for _ in range(5):
        _append_with_sleep(memory, "NIFTY", MarketRegime.RANGING, 0.6)

    stability = RegimeStability(memory)

    score = stability.stability_score("NIFTY")
    assert 0.0 <= score <= 1.0


def test_confidence_trend_stats():
    memory = RegimeMemory()

    _append_with_sleep(memory, "NIFTY", MarketRegime.RANGING, 0.4)
    _append_with_sleep(memory, "NIFTY", MarketRegime.RANGING, 0.8)
    _append_with_sleep(memory, "NIFTY", MarketRegime.RANGING, 0.6)

    stability = RegimeStability(memory)

    stats = stability.confidence_trend("NIFTY")

    assert stats["min"] == 0.4
    assert stats["max"] == 0.8
    assert abs(stats["mean"] - 0.6) < 1e-6


def test_metrics_do_not_mutate_memory():
    memory = RegimeMemory()

    _append_with_sleep(memory, "NIFTY", MarketRegime.RANGING, 0.6)
    initial_count = memory.count()

    stability = RegimeStability(memory)
    _ = stability.stability_score("NIFTY")
    _ = stability.average_regime_duration("NIFTY")

    assert memory.count() == initial_count
