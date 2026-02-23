from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Union

from core.dashboard_read.snapshot import SystemSnapshot
from core.dashboard_read.evidence.record import EvidenceRecord
from core.dashboard_read.migrations import migrate_snapshot_payload


class SnapshotPersistenceError(RuntimeError):
    """
    Raised when snapshot serialization or deserialization fails.
    """
    pass


# ---------------------------------------------------------------------
# SERIALIZATION
# ---------------------------------------------------------------------

def snapshot_to_dict(snapshot: SystemSnapshot) -> Dict[str, Any]:
    """
    Canonical, JSON-safe serialization.
    Providers are NEVER called here.
    """
    payload = snapshot.to_dict()

    if "meta" not in payload or not isinstance(payload["meta"], dict):
        raise SnapshotPersistenceError("Snapshot serialization missing meta block")

    return payload


def snapshot_to_json(
    snapshot: SystemSnapshot,
    *,
    path: Union[str, Path] | None = None,
) -> str:
    """
    Serialize snapshot + evidence into a canonical JSON envelope.

    CONTRACT:
    - Top-level "meta" MUST always exist (forward compatibility)
    - Snapshot payload is immutable
    """
    snapshot_payload = snapshot_to_dict(snapshot)

    envelope: Dict[str, Any] = {
        "meta": {},  # 🔒 ALWAYS PRESENT
        "snapshot": snapshot_payload,
        "evidence": EvidenceRecord.create(snapshot_payload).__dict__,
    }

    blob = json.dumps(envelope, sort_keys=True, ensure_ascii=False)

    if path is not None:
        Path(path).write_text(blob, encoding="utf-8")

    return blob


# ---------------------------------------------------------------------
# DESERIALIZATION
# ---------------------------------------------------------------------

def snapshot_from_dict(payload: Dict[str, Any]) -> SystemSnapshot:
    """
    Provider-free reconstruction from dict.
    Applies schema migrations before materialization.
    """
    migrated = migrate_snapshot_payload(payload)

    migrated.setdefault("meta", {})
    if not isinstance(migrated.get("meta"), dict):
        migrated["meta"] = {}

    return SystemSnapshot.from_dict(migrated)


def snapshot_from_json(blob: str) -> SystemSnapshot:
    """
    Load snapshot from canonical JSON envelope.
    Evidence is verified separately; snapshot reconstruction is pure.
    """
    raw = json.loads(blob)

    # 🔒 Envelope meta MUST exist (forward compatibility)
    raw.setdefault("meta", {})
    if not isinstance(raw.get("meta"), dict):
        raw["meta"] = {}

    snapshot_payload = raw.get("snapshot")
    if not isinstance(snapshot_payload, dict):
        raise SnapshotPersistenceError("Missing snapshot payload")

    snapshot_payload = snapshot_payload.copy()
    snapshot_payload.setdefault("meta", {})
    if not isinstance(snapshot_payload.get("meta"), dict):
        snapshot_payload["meta"] = {}

    migrated = migrate_snapshot_payload(snapshot_payload)

    migrated.setdefault("meta", {})
    if not isinstance(migrated.get("meta"), dict):
        migrated["meta"] = {}

    return SystemSnapshot.from_dict(migrated)
