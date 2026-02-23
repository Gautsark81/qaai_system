# tests/context/test_context_governance.py

import pytest
from copy import deepcopy

from core.regime.regime_memory import RegimeMemory
from core.regime.regime_types import MarketRegime
from core.regime.regime_context import RegimeContext
from core.context.context_wiring import StrategyContextProvider


# ---------------------------------------------------------------------
# Test setup helpers
# ---------------------------------------------------------------------

def _setup_context():
    memory = RegimeMemory()
    memory.append(
        symbol="NIFTY",
        regime=MarketRegime.TRENDING,
        confidence=0.82,
        detector_id="regime_detector_v1",
        evidence={},
    )

    base = RegimeContext(memory)
    return StrategyContextProvider(base)


# ---------------------------------------------------------------------
# Phase-5.4 — Context Governance Tests
# ---------------------------------------------------------------------

def test_context_exposes_governance_notes_channel():
    """
    Context snapshot must expose a governance_notes channel.
    """
    provider = _setup_context()
    snap = provider.get("NIFTY")

    assert "governance_notes" in snap
    assert isinstance(snap["governance_notes"], (list, tuple))


def test_governance_notes_empty_by_default():
    """
    Governance notes must start empty.
    """
    provider = _setup_context()
    snap = provider.get("NIFTY")

    assert len(snap["governance_notes"]) == 0


def test_governance_note_can_be_attached_non_binding():
    """
    Attaching a governance note must NOT affect context values.
    """
    provider = _setup_context()
    snap = provider.get("NIFTY")

    # capture baseline context
    baseline = deepcopy({k: v for k, v in snap.items() if k != "governance_notes"})

    note = {
        "note": "High volatility regime — monitor risk",
        "severity": "WARN",
        "author": "risk_officer",
    }

    snap["governance_notes"].append(note)

    assert len(snap["governance_notes"]) == 1

    # context payload must remain unchanged
    after = {k: v for k, v in snap.items() if k != "governance_notes"}
    assert after == baseline


def test_governance_notes_are_append_only():
    """
    Governance notes must not be removable or mutable.
    """
    provider = _setup_context()
    snap = provider.get("NIFTY")

    snap["governance_notes"].append(
        {"note": "Test", "severity": "INFO", "author": "system"}
    )

    with pytest.raises((TypeError, AttributeError)):
        snap["governance_notes"].pop()

    with pytest.raises((TypeError, AttributeError)):
        snap["governance_notes"].clear()


def test_governance_notes_are_read_only_structures():
    """
    Individual governance notes must be immutable.
    """
    provider = _setup_context()
    snap = provider.get("NIFTY")

    snap["governance_notes"].append(
        {"note": "Audit marker", "severity": "INFO", "author": "audit"}
    )

    note = snap["governance_notes"][0]

    with pytest.raises(TypeError):
        note["severity"] = "CRITICAL"


def test_governance_notes_reference_context_hash():
    """
    Governance notes must reference the context hash they annotate.
    """
    provider = _setup_context()
    snap = provider.get("NIFTY")

    snap["governance_notes"].append(
        {
            "note": "Trend continuation expected",
            "severity": "INFO",
            "author": "strategy_lead",
        }
    )

    note = snap["governance_notes"][0]

    assert "context_hash" in note
    assert note["context_hash"] == snap["lineage"].snapshot_hash


def test_governance_export_is_serializable_and_read_only():
    """
    Governance notes must be exportable for audit.
    """
    provider = _setup_context()
    snap = provider.get("NIFTY")

    snap["governance_notes"].append(
        {"note": "Audit export test", "severity": "INFO", "author": "audit"}
    )

    exported = snap["governance_notes"]

    assert isinstance(exported, (list, tuple))

    with pytest.raises(TypeError):
        exported.append({"note": "illegal"})


def test_governance_has_no_execution_effect():
    """
    Governance notes must not alter context interpretation.
    """
    provider = _setup_context()
    snap = provider.get("NIFTY")

    snap["governance_notes"].append(
        {"note": "No trade during news", "severity": "WARN", "author": "human"}
    )

    # regime data must remain unchanged
    assert snap["current_regime"] == MarketRegime.TRENDING
    assert snap["stability_score"] >= 0.0
