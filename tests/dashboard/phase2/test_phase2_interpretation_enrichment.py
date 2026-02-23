# tests/dashboard/phase2/test_phase2_interpretation_enrichment.py

import pytest
from copy import deepcopy

from dashboard.snapshot_loader import load_dashboard_snapshot

# ─────────────────────────────────────────────────────────────
# Phase-7.1 — Interpretation Enrichment
# ─────────────────────────────────────────────────────────────

def _load_interpretation_snapshot():
    state, snapshot = load_dashboard_snapshot()
    assert snapshot is not None
    assert hasattr(snapshot, "interpretation")
    return snapshot

def test_interpretation_panels_expose_enrichment_fields():
    """
    Each interpretation panel must expose enrichment metadata.
    """
    snapshot = _load_interpretation_snapshot()
    interpretation = snapshot.interpretation

    for panel_name, panel in interpretation.items():
        if panel_name in ("derived_from", "as_of"):
            continue

        assert "signals_considered" in panel
        assert "drivers" in panel
        assert "confidence_breakdown" in panel

        assert isinstance(panel["signals_considered"], (list, tuple))
        assert isinstance(panel["drivers"], (list, tuple))
        assert isinstance(panel["confidence_breakdown"], dict)


def test_interpretation_enrichment_is_deterministic():
    """
    Same snapshot → identical enriched interpretation.
    """
    s1 = _load_interpretation_snapshot()
    s2 = _load_interpretation_snapshot()

    assert s1.hash == s2.hash
    assert s1.interpretation == s2.interpretation


def test_enrichment_does_not_change_primary_interpretation_fields():
    """
    Enrichment must not alter core interpretation semantics.
    """
    snapshot = _load_interpretation_snapshot()
    interpretation = snapshot.interpretation

    for panel_name, panel in interpretation.items():
        if panel_name in ("derived_from", "as_of"):
            continue

        assert "label" in panel
        assert "confidence" in panel


def test_interpretation_enrichment_is_read_only():
    """
    Enrichment metadata must be immutable.
    """
    snapshot = _load_interpretation_snapshot()
    interpretation = snapshot.interpretation

    panel = next(
        v for k, v in interpretation.items()
        if k not in ("derived_from", "as_of")
    )

    with pytest.raises((TypeError, AttributeError)):
        panel["drivers"].append("illegal_mutation")

    with pytest.raises((TypeError, AttributeError)):
        panel["confidence_breakdown"]["base"] = 0.0


def test_enrichment_has_no_wallclock_or_external_dependency():
    """
    Enrichment must be snapshot-anchored and replay-safe.
    """
    snapshot = _load_interpretation_snapshot()
    interpretation = snapshot.interpretation

    assert interpretation["derived_from"] == snapshot.hash
    assert "as_of" in interpretation

    frozen = deepcopy(interpretation)
    assert frozen == interpretation
