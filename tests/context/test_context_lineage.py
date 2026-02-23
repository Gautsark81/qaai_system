# tests/context/test_context_lineage.py

import pytest
from datetime import datetime, timezone

from core.regime.regime_memory import RegimeMemory
from core.regime.regime_types import MarketRegime
from core.regime.regime_context import RegimeContext
from core.context.context_wiring import StrategyContextProvider
from core.context.context_lineage import ContextLineage


def _setup_context():
    memory = RegimeMemory()
    memory.append(
        symbol="NIFTY",
        regime=MarketRegime.TRENDING,
        confidence=0.82,
        detector_id="regime_detector_v1",
        evidence={"volatility": "expanding"},
    )

    base = RegimeContext(memory)
    provider = StrategyContextProvider(base)
    return provider


def test_lineage_is_attached_to_context_snapshot():
    provider = _setup_context()
    snap = provider.get("NIFTY")

    assert "lineage" in snap
    assert isinstance(snap["lineage"], ContextLineage)


def test_lineage_contains_provenance_fields():
    provider = _setup_context()
    lineage = provider.get("NIFTY")["lineage"]

    assert lineage.symbol == "NIFTY"
    assert lineage.source == "RegimeMemory"
    assert lineage.detector_ids == ["regime_detector_v1"]
    assert lineage.regimes == [MarketRegime.TRENDING]
    assert isinstance(lineage.snapshot_hash, str)


def test_lineage_is_deterministic_for_same_memory_state():
    provider1 = _setup_context()
    provider2 = _setup_context()

    l1 = provider1.get("NIFTY")["lineage"]
    l2 = provider2.get("NIFTY")["lineage"]

    assert l1 == l2


def test_lineage_is_immutable():
    provider = _setup_context()
    lineage = provider.get("NIFTY")["lineage"]

    with pytest.raises(Exception):
        lineage.symbol = "BANKNIFTY"


def test_lineage_does_not_affect_context_payload():
    provider = _setup_context()
    snap = provider.get("NIFTY")

    assert snap["current_regime"] == MarketRegime.TRENDING
    assert snap["stability_score"] >= 0.0


def test_lineage_is_exportable_for_audit():
    provider = _setup_context()
    lineage = provider.get("NIFTY")["lineage"]

    exported = lineage.export()

    assert isinstance(exported, dict)
    assert exported["symbol"] == "NIFTY"
    assert exported["source"] == "RegimeMemory"
    assert exported["detector_ids"] == ["regime_detector_v1"]
    assert exported["regimes"] == ["TRENDING"]
    assert "snapshot_hash" in exported


def test_lineage_export_is_read_only():
    provider = _setup_context()
    exported = provider.get("NIFTY")["lineage"].export()

    with pytest.raises(TypeError):
        exported["symbol"] = "BANKNIFTY"


def test_lineage_has_no_wallclock_time_dependency():
    provider = _setup_context()
    lineage = provider.get("NIFTY")["lineage"]

    assert not hasattr(lineage, "created_at") or lineage.created_at is None
