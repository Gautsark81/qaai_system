from core.regime.regime_memory import RegimeMemory
from core.regime.regime_types import MarketRegime
from core.regime.regime_context import RegimeContext
from core.regime.context_contracts import (
    StrategyContextView,
    MetaModelContextView,
    ObservabilityContextView,
)


def _append(memory, symbol, regime, confidence=0.6):
    memory.append(
        symbol=symbol,
        regime=regime,
        confidence=confidence,
        detector_id="test",
        evidence={},
    )


def test_strategy_context_view_is_restricted():
    memory = RegimeMemory()
    _append(memory, "NIFTY", MarketRegime.RANGING)

    base = RegimeContext(memory)
    view = StrategyContextView(base)

    snap = view.snapshot("NIFTY")

    assert "current_regime" in snap
    assert "stability_score" in snap

    # Must NOT expose deeper metrics
    assert "switch_count" not in snap
    assert "confidence_stats" not in snap
    assert "dominant_transition" not in snap


def test_meta_model_context_view_expands_strategy_view():
    memory = RegimeMemory()
    _append(memory, "NIFTY", MarketRegime.RANGING, 0.4)
    _append(memory, "NIFTY", MarketRegime.TRENDING, 0.8)

    base = RegimeContext(memory)
    view = MetaModelContextView(base)

    snap = view.snapshot("NIFTY")

    assert "current_regime" in snap
    assert "stability_score" in snap
    assert "switch_count" in snap
    assert "transition_frequency" in snap
    assert "confidence_stats" in snap

    # Still must NOT expose dominant transition
    assert "dominant_transition" not in snap


def test_observability_context_view_is_superset():
    memory = RegimeMemory()
    _append(memory, "NIFTY", MarketRegime.RANGING)
    _append(memory, "NIFTY", MarketRegime.TRENDING)

    base = RegimeContext(memory)
    view = ObservabilityContextView(base)

    snap = view.snapshot("NIFTY")

    assert "current_regime" in snap
    assert "stability_score" in snap
    assert "switch_count" in snap
    assert "transition_frequency" in snap
    assert "confidence_stats" in snap
    assert "dominant_transition" in snap


def test_all_context_views_are_read_only():
    memory = RegimeMemory()
    _append(memory, "NIFTY", MarketRegime.RANGING)

    base = RegimeContext(memory)

    for view_cls in (
        StrategyContextView,
        MetaModelContextView,
        ObservabilityContextView,
    ):
        snap = view_cls(base).snapshot("NIFTY")
        try:
            snap["current_regime"] = MarketRegime.TRENDING
            mutated = True
        except Exception:
            mutated = False

        assert mutated is False
