import copy
import pytest

from core.dashboard_read.migrations import (
    migrate_snapshot_payload,
    CURRENT_SNAPSHOT_SCHEMA_VERSION,
    SnapshotMigrationError,
)
from core.dashboard_read.persistence import (
    snapshot_to_json,
    snapshot_from_json,
)
from core.dashboard_read.builder import SystemSnapshotBuilder


# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------

def _build_snapshot():
    builder = SystemSnapshotBuilder(
        execution_mode="offline",
        market_status="closed",
        system_version="v1",
    )
    return builder.build()


# ---------------------------------------------------------------------
# D-4.7 — SCHEMA VERSIONING TESTS
# ---------------------------------------------------------------------

def test_snapshot_contains_schema_version():
    snap = _build_snapshot()

    assert snap.meta.schema_version == CURRENT_SNAPSHOT_SCHEMA_VERSION
    assert isinstance(snap.meta.schema_version, int)


def test_schema_version_persists_through_serialization():
    snap = _build_snapshot()

    blob = snapshot_to_json(snap)
    snap2 = snapshot_from_json(blob)

    assert snap2.meta.schema_version == CURRENT_SNAPSHOT_SCHEMA_VERSION


def test_migration_adds_schema_version_if_missing():
    snap = _build_snapshot()
    payload = snap.to_dict()

    # simulate legacy snapshot (v0)
    legacy = copy.deepcopy(payload)
    legacy["meta"].pop("schema_version", None)

    migrated = migrate_snapshot_payload(legacy)

    assert "schema_version" in migrated["meta"]
    assert migrated["meta"]["schema_version"] == CURRENT_SNAPSHOT_SCHEMA_VERSION


def test_migration_is_idempotent():
    snap = _build_snapshot()
    payload = snap.to_dict()

    migrated_once = migrate_snapshot_payload(payload)
    migrated_twice = migrate_snapshot_payload(migrated_once)

    assert migrated_once == migrated_twice


def test_unknown_schema_version_is_rejected():
    snap = _build_snapshot()
    payload = snap.to_dict()

    payload["meta"]["schema_version"] = 999

    with pytest.raises(SnapshotMigrationError):
        migrate_snapshot_payload(payload)


def test_migration_does_not_mutate_input():
    snap = _build_snapshot()
    payload = snap.to_dict()

    legacy = copy.deepcopy(payload)
    legacy["meta"].pop("schema_version", None)

    before = copy.deepcopy(legacy)
    _ = migrate_snapshot_payload(legacy)

    assert legacy == before


def test_deserialization_uses_migration_path(monkeypatch):
    """
    Guarantee:
    snapshot_from_json must tolerate older schemas
    WITHOUT calling providers.
    """

    def explode():
        raise RuntimeError("provider access forbidden")

    monkeypatch.setattr(
        "core.dashboard_read.providers.market_state.build_market_state",
        explode,
    )

    snap = _build_snapshot()
    payload = snap.to_dict()

    # simulate v0 snapshot
    payload["meta"].pop("schema_version", None)

    blob = snapshot_to_json(snap)
    snap2 = snapshot_from_json(blob)

    assert snap2.meta.schema_version == CURRENT_SNAPSHOT_SCHEMA_VERSION


def test_schema_version_not_part_of_fingerprint():
    """
    Fingerprint must represent semantic system state,
    not schema bookkeeping.
    """
    snap = _build_snapshot()
    blob = snapshot_to_json(snap)
    snap2 = snapshot_from_json(blob)

    assert snap.meta.fingerprint == snap2.meta.fingerprint
