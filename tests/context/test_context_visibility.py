from core.regime.regime_memory import RegimeMemory
from core.regime.regime_types import MarketRegime
from core.regime.regime_context import RegimeContext
from core.context.context_wiring import StrategyContextProvider
from core.context.context_visibility import ContextVisibilitySurface


def _setup_context():
    memory = RegimeMemory()
    memory.append(
        symbol="NIFTY",
        regime=MarketRegime.TRENDING,
        confidence=0.85,
        detector_id="test",
        evidence={},
    )

    base = RegimeContext(memory)
    return StrategyContextProvider(base)


def test_context_can_be_exported_for_audit():
    provider = _setup_context()
    surface = ContextVisibilitySurface(provider)

    snapshot = surface.export(symbol="NIFTY")

    assert snapshot["current_regime"] == MarketRegime.TRENDING
    assert "stability_score" in snapshot


def test_exported_context_is_read_only():
    provider = _setup_context()
    surface = ContextVisibilitySurface(provider)

    snapshot = surface.export(symbol="NIFTY")

    try:
        snapshot["current_regime"] = MarketRegime.RANGING
        mutated = True
    except Exception:
        mutated = False

    assert mutated is False


def test_context_export_is_deterministic():
    provider = _setup_context()
    surface = ContextVisibilitySurface(provider)

    s1 = surface.export(symbol="NIFTY")
    s2 = surface.export(symbol="NIFTY")

    assert s1 == s2


def test_visibility_surface_handles_missing_context():
    surface = ContextVisibilitySurface(provider=None)

    snapshot = surface.export(symbol="NIFTY")

    assert snapshot is None
