import pytest
from copy import deepcopy

from core.regime.regime_memory import RegimeMemory
from core.regime.regime_context import RegimeContext
from core.regime.regime_types import MarketRegime
from core.context.context_wiring import StrategyContextProvider


# ─────────────────────────────────────────────
# Test setup (canonical)
# ─────────────────────────────────────────────

def _setup_context():
    memory = RegimeMemory()
    memory.append(
        symbol="NIFTY",
        regime=MarketRegime.TRENDING,
        confidence=0.8,
        detector_id="regime_detector_v1",
        evidence={},
    )

    base = RegimeContext(memory)
    return StrategyContextProvider(base)


# ─────────────────────────────────────────────
# Phase-7.0 — Capital Advisory Surface (Tests)
# ─────────────────────────────────────────────

def test_context_exposes_capital_advisory():
    provider = _setup_context()
    snap = provider.get("NIFTY")

    assert "capital_advisory" in snap


def test_capital_advisory_is_dict_like():
    provider = _setup_context()
    advisory = provider.get("NIFTY")["capital_advisory"]

    assert isinstance(advisory, dict)


def test_capital_advisory_has_required_fields():
    provider = _setup_context()
    advisory = provider.get("NIFTY")["capital_advisory"]

    required = {
        "recommended_exposure",
        "confidence",
        "rationale",
        "constraints",
        "source",
    }

    assert required.issubset(advisory.keys())


def test_capital_advisory_is_read_only():
    provider = _setup_context()
    advisory = provider.get("NIFTY")["capital_advisory"]

    with pytest.raises(TypeError):
        advisory["confidence"] = 0.25


def test_capital_advisory_is_deterministic():
    p1 = _setup_context()
    p2 = _setup_context()

    a1 = p1.get("NIFTY")["capital_advisory"]
    a2 = p2.get("NIFTY")["capital_advisory"]

    assert a1 == a2


def test_capital_advisory_references_capital_view():
    provider = _setup_context()
    advisory = provider.get("NIFTY")["capital_advisory"]

    assert advisory["source"] == "capital_view"


def test_capital_advisory_does_not_affect_context():
    provider = _setup_context()
    snap = provider.get("NIFTY")

    baseline = deepcopy(
        {k: v for k, v in snap.items() if k != "capital_advisory"}
    )

    _ = snap["capital_advisory"]

    after = {k: v for k, v in snap.items() if k != "capital_advisory"}

    assert baseline == after


def test_capital_advisory_does_not_affect_execution_fields():
    provider = _setup_context()
    snap = provider.get("NIFTY")

    _ = snap["capital_advisory"]

    assert snap["current_regime"] == MarketRegime.TRENDING
    assert snap["stability_score"] > 0


def test_capital_advisory_is_export_safe():
    provider = _setup_context()
    advisory = provider.get("NIFTY")["capital_advisory"]

    exported = dict(advisory)

    assert isinstance(exported, dict)
    assert exported["recommended_exposure"] in {
        "LOW",
        "NORMAL",
        "REDUCED",
        "BLOCK",
    }
