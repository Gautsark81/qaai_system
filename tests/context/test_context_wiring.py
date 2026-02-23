from core.regime.regime_memory import RegimeMemory
from core.regime.regime_types import MarketRegime
from core.regime.regime_context import RegimeContext
from core.context.context_wiring import (
    StrategyContextProvider,
    MetaModelContextProvider,
    ObservabilityContextProvider,
)


def _append(memory, symbol, regime, confidence=0.6):
    memory.append(
        symbol=symbol,
        regime=regime,
        confidence=confidence,
        detector_id="test",
        evidence={},
    )


def test_strategy_context_provider_is_restricted():
    memory = RegimeMemory()
    _append(memory, "NIFTY", MarketRegime.RANGING)

    base = RegimeContext(memory)
    provider = StrategyContextProvider(base)

    snap = provider.get("NIFTY")

    assert "current_regime" in snap
    assert "stability_score" in snap
    assert "switch_count" not in snap


def test_meta_model_context_provider_is_expanded():
    memory = RegimeMemory()
    _append(memory, "NIFTY", MarketRegime.RANGING)
    _append(memory, "NIFTY", MarketRegime.TRENDING)

    base = RegimeContext(memory)
    provider = MetaModelContextProvider(base)

    snap = provider.get("NIFTY")

    assert "switch_count" in snap
    assert "confidence_stats" in snap
    assert "dominant_transition" not in snap


def test_observability_context_provider_is_superset():
    memory = RegimeMemory()
    _append(memory, "NIFTY", MarketRegime.RANGING)
    _append(memory, "NIFTY", MarketRegime.TRENDING)

    base = RegimeContext(memory)
    provider = ObservabilityContextProvider(base)

    snap = provider.get("NIFTY")

    assert "dominant_transition" in snap


def test_providers_do_not_expose_base_context():
    memory = RegimeMemory()
    _append(memory, "NIFTY", MarketRegime.RANGING)

    base = RegimeContext(memory)
    provider = StrategyContextProvider(base)

    assert not hasattr(provider, "_memory")
    assert not hasattr(provider, "_base_context")


def test_wiring_is_read_only():
    memory = RegimeMemory()
    _append(memory, "NIFTY", MarketRegime.RANGING)

    base = RegimeContext(memory)
    provider = StrategyContextProvider(base)

    snap = provider.get("NIFTY")

    try:
        snap["current_regime"] = MarketRegime.TRENDING
        mutated = True
    except Exception:
        mutated = False

    assert mutated is False
