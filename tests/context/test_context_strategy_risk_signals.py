import pytest
from copy import deepcopy

from core.regime.regime_memory import RegimeMemory
from core.regime.regime_types import MarketRegime
from core.regime.regime_context import RegimeContext
from core.context.context_wiring import StrategyContextProvider


# ---------------------------------------------------------------------
# Test setup
# ---------------------------------------------------------------------

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


# ---------------------------------------------------------------------
# Phase-6.3 — Strategy-Facing Risk Signals (Advisory Only)
# ---------------------------------------------------------------------

def test_context_exposes_strategy_risk_signals():
    """
    Strategy context must expose a risk_signals channel.
    """
    provider = _setup_context()
    snap = provider.get("NIFTY")

    assert "risk_signals" in snap


def test_risk_signals_is_dict_like():
    """
    Risk signals must be presented as a dictionary-like structure.
    """
    provider = _setup_context()
    signals = provider.get("NIFTY")["risk_signals"]

    assert isinstance(signals, dict)


def test_risk_signals_has_required_fields():
    """
    Risk signals must expose a minimal, stable advisory contract.
    """
    provider = _setup_context()
    signals = provider.get("NIFTY")["risk_signals"]

    required = {
        "risk_level",
        "confidence",
        "advisory",
        "source",
    }

    assert required.issubset(signals.keys())


def test_risk_signals_are_advisory_only():
    """
    Risk signals must not be execution-binding.
    """
    provider = _setup_context()
    signals = provider.get("NIFTY")["risk_signals"]

    assert signals["advisory"] is True


def test_risk_signals_are_read_only():
    """
    Strategy must not be able to mutate risk signals.
    """
    provider = _setup_context()
    signals = provider.get("NIFTY")["risk_signals"]

    with pytest.raises(TypeError):
        signals["risk_level"] = "HIGH"


def test_risk_signals_are_deterministic():
    """
    Same context state must produce identical risk signals.
    """
    p1 = _setup_context()
    p2 = _setup_context()

    s1 = p1.get("NIFTY")["risk_signals"]
    s2 = p2.get("NIFTY")["risk_signals"]

    assert dict(s1) == dict(s2)


def test_risk_signals_do_not_affect_context_snapshot():
    """
    Accessing risk signals must not mutate context.
    """
    provider = _setup_context()
    snap = provider.get("NIFTY")

    baseline = deepcopy(
        {k: v for k, v in snap.items() if k != "risk_signals"}
    )

    _ = snap["risk_signals"]

    after = {k: v for k, v in snap.items() if k != "risk_signals"}

    assert baseline == after


def test_risk_signals_reference_risk_view():
    """
    Risk signals must clearly state their derivation source.
    """
    provider = _setup_context()
    signals = provider.get("NIFTY")["risk_signals"]

    assert signals["source"] == "risk_view"


def test_risk_signals_are_export_safe():
    """
    Risk signals must be serialization-safe for audit/logging.
    """
    provider = _setup_context()
    signals = provider.get("NIFTY")["risk_signals"]

    exported = dict(signals)

    assert isinstance(exported, dict)
    assert "risk_level" in exported
    assert "confidence" in exported
