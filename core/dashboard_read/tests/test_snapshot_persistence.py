import pytest

from core.dashboard_read.builder import SystemSnapshotBuilder
from core.dashboard_read.persistence import (
    snapshot_to_json,
    snapshot_from_json,
)


def _build_snapshot():
    return SystemSnapshotBuilder(
        execution_mode="paper",
        market_status="open",
        system_version="v1",
    ).build()


def test_snapshot_roundtrip_identity():
    snap1 = _build_snapshot()
    blob = snapshot_to_json(snap1)
    snap2 = snapshot_from_json(blob)

    assert snap1.meta.snapshot_id != snap2.meta.snapshot_id
    assert snap1.meta.execution_mode == snap2.meta.execution_mode
    assert snap1.system_health == snap2.system_health


def test_snapshot_fingerprint_survives_serialization():
    snap1 = _build_snapshot()
    blob = snapshot_to_json(snap1)
    snap2 = snapshot_from_json(blob)

    assert snap1.fingerprint == snap2.fingerprint


def test_snapshot_deserialize_does_not_call_providers(monkeypatch):
    def explode():
        raise RuntimeError("provider access forbidden")

    monkeypatch.setattr(
        "core.dashboard_read.providers.market_state.build_market_state",
        explode,
    )

    snap = _build_snapshot()
    blob = snapshot_to_json(snap)

    # Must NOT touch providers
    snapshot_from_json(blob)


def test_snapshot_backward_compatible_load():
    snap = _build_snapshot()
    blob = snapshot_to_json(snap)

    import json
    payload = json.loads(blob)
    payload["meta"]["future_field"] = "ignore_me"

    blob2 = json.dumps(payload)
    snap2 = snapshot_from_json(blob2)

    assert snap2.meta.execution_mode == snap.meta.execution_mode
