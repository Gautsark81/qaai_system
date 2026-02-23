from core.regime.regime_memory import RegimeMemory
from core.regime.regime_types import MarketRegime
from core.regime.regime_context import RegimeContext


def _append(memory, symbol, regime, confidence=0.6):
    memory.append(
        symbol=symbol,
        regime=regime,
        confidence=confidence,
        detector_id="test",
        evidence={},
    )


def test_context_exposes_current_regime():
    memory = RegimeMemory()
    _append(memory, "NIFTY", MarketRegime.RANGING)

    ctx = RegimeContext(memory)
    snapshot = ctx.snapshot("NIFTY")

    assert snapshot["current_regime"] == MarketRegime.RANGING


def test_context_exposes_stability_metrics():
    memory = RegimeMemory()

    _append(memory, "NIFTY", MarketRegime.RANGING)
    _append(memory, "NIFTY", MarketRegime.TRENDING)
    _append(memory, "NIFTY", MarketRegime.RANGING)

    ctx = RegimeContext(memory)
    snap = ctx.snapshot("NIFTY")

    assert 0.0 <= snap["stability_score"] <= 1.0
    assert snap["switch_count"] == 2
    assert 0.0 < snap["transition_frequency"] <= 1.0


def test_context_exposes_transition_structure():
    memory = RegimeMemory()

    _append(memory, "NIFTY", MarketRegime.RANGING)
    _append(memory, "NIFTY", MarketRegime.TRENDING)

    ctx = RegimeContext(memory)
    snap = ctx.snapshot("NIFTY")

    assert snap["dominant_transition"] == (
        MarketRegime.RANGING,
        MarketRegime.TRENDING,
    )


def test_context_exposes_confidence_stats():
    memory = RegimeMemory()

    _append(memory, "NIFTY", MarketRegime.RANGING, 0.4)
    _append(memory, "NIFTY", MarketRegime.RANGING, 0.8)

    ctx = RegimeContext(memory)
    snap = ctx.snapshot("NIFTY")

    stats = snap["confidence_stats"]
    assert stats["min"] == 0.4
    assert stats["max"] == 0.8
    assert abs(stats["mean"] - 0.6) < 1e-6


def test_context_is_read_only():
    memory = RegimeMemory()
    _append(memory, "NIFTY", MarketRegime.RANGING)

    ctx = RegimeContext(memory)
    snap = ctx.snapshot("NIFTY")

    try:
        snap["current_regime"] = MarketRegime.TRENDING
        mutated = True
    except Exception:
        mutated = False

    assert mutated is False
