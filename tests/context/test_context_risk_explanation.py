from copy import deepcopy
import pytest

from core.regime.regime_types import MarketRegime


def _setup_context():
    from core.regime.regime_memory import RegimeMemory
    from core.regime.regime_context import RegimeContext
    from core.context.context_wiring import StrategyContextProvider

    memory = RegimeMemory()
    memory.append(
        symbol="NIFTY",
        regime=MarketRegime.TRENDING,
        confidence=0.82,
        detector_id="regime_detector_v1",
        evidence={"trend_strength": "high"},
    )

    base = RegimeContext(memory)
    return StrategyContextProvider(base)


# ─────────────────────────────────────────────
# Phase-6.1 — Risk Explanation Hooks
# ─────────────────────────────────────────────

def test_context_exposes_risk_explanation():
    provider = _setup_context()
    snap = provider.get("NIFTY")

    assert "risk_explanation" in snap


def test_risk_explanation_is_dict_like():
    provider = _setup_context()
    explanation = provider.get("NIFTY")["risk_explanation"]

    assert isinstance(explanation, dict)


def test_risk_explanation_has_required_fields():
    provider = _setup_context()
    explanation = provider.get("NIFTY")["risk_explanation"]

    for field in (
        "summary",
        "drivers",
        "assumptions",
        "confidence",
        "derived_from",
    ):
        assert field in explanation


def test_risk_explanation_is_read_only():
    provider = _setup_context()
    explanation = provider.get("NIFTY")["risk_explanation"]

    with pytest.raises(TypeError):
        explanation["summary"] = "mutate"


def test_risk_explanation_is_deterministic():
    p1 = _setup_context()
    p2 = _setup_context()

    e1 = p1.get("NIFTY")["risk_explanation"]
    e2 = p2.get("NIFTY")["risk_explanation"]

    assert e1 == e2


def test_risk_explanation_matches_risk_view():
    provider = _setup_context()
    snap = provider.get("NIFTY")

    explanation = snap["risk_explanation"]
    risk_view = snap["risk_view"]

    assert explanation["confidence"] == risk_view["confidence"]
    assert risk_view["risk_regime"].lower() in explanation["summary"].lower()


def test_risk_explanation_does_not_affect_context():
    provider = _setup_context()
    snap = provider.get("NIFTY")

    baseline = deepcopy(
        {k: v for k, v in snap.items() if k != "risk_explanation"}
    )

    _ = snap["risk_explanation"]

    assert baseline == {
        k: v for k, v in snap.items() if k != "risk_explanation"
    }


def test_risk_explanation_is_export_safe():
    provider = _setup_context()
    explanation = provider.get("NIFTY")["risk_explanation"]

    exported = dict(explanation)

    assert isinstance(exported, dict)
    assert exported["derived_from"] == "risk_view"
