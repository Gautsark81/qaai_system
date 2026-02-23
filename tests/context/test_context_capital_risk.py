# tests/context/test_context_capital_risk.py

from copy import deepcopy
import pytest

from core.regime.regime_memory import RegimeMemory
from core.regime.regime_types import MarketRegime
from core.regime.regime_context import RegimeContext
from core.context.context_wiring import StrategyContextProvider


def _setup_context():
    memory = RegimeMemory()
    memory.append(
        symbol="NIFTY",
        regime=MarketRegime.TRENDING,
        confidence=0.85,
        detector_id="regime_detector_v1",
        evidence={},
    )
    base = RegimeContext(memory)
    return StrategyContextProvider(base)


# ─────────────────────────────────────────────
# Capital View
# ─────────────────────────────────────────────

def test_context_exposes_capital_view():
    provider = _setup_context()
    snap = provider.get("NIFTY")

    assert "capital_view" in snap
    assert isinstance(snap["capital_view"], dict)


def test_capital_view_has_required_fields():
    provider = _setup_context()
    view = provider.get("NIFTY")["capital_view"]

    assert "utilization_band" in view
    assert "confidence" in view
    assert "note" in view


def test_capital_view_is_read_only():
    provider = _setup_context()
    view = provider.get("NIFTY")["capital_view"]

    with pytest.raises(TypeError):
        view["confidence"] = 0.1


def test_capital_view_is_deterministic():
    p1 = _setup_context()
    p2 = _setup_context()

    v1 = p1.get("NIFTY")["capital_view"]
    v2 = p2.get("NIFTY")["capital_view"]

    assert v1 == v2


# ─────────────────────────────────────────────
# Risk View
# ─────────────────────────────────────────────

def test_context_exposes_risk_view():
    provider = _setup_context()
    snap = provider.get("NIFTY")

    assert "risk_view" in snap
    assert isinstance(snap["risk_view"], dict)


def test_risk_view_has_required_fields():
    provider = _setup_context()
    view = provider.get("NIFTY")["risk_view"]

    assert "risk_regime" in view
    assert "confidence" in view
    assert "note" in view


def test_risk_view_is_read_only():
    provider = _setup_context()
    view = provider.get("NIFTY")["risk_view"]

    with pytest.raises(TypeError):
        view["risk_regime"] = "CRISIS"


def test_risk_view_is_deterministic():
    p1 = _setup_context()
    p2 = _setup_context()

    v1 = p1.get("NIFTY")["risk_view"]
    v2 = p2.get("NIFTY")["risk_view"]

    assert v1 == v2


# ─────────────────────────────────────────────
# Safety Invariants
# ─────────────────────────────────────────────

def test_capital_and_risk_views_do_not_affect_core_context():
    provider = _setup_context()
    snap = provider.get("NIFTY")

    baseline = deepcopy(
        {k: v for k, v in snap.items() if k not in ("capital_view", "risk_view")}
    )

    _ = snap["capital_view"]
    _ = snap["risk_view"]

    after = {k: v for k, v in snap.items() if k not in ("capital_view", "risk_view")}

    assert baseline == after
