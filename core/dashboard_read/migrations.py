from __future__ import annotations

from typing import Any, Dict


# ---------------------------------------------------------------------
# SNAPSHOT SCHEMA VERSIONING
# ---------------------------------------------------------------------

CURRENT_SNAPSHOT_SCHEMA_VERSION = 1


class SnapshotMigrationError(RuntimeError):
    pass


def migrate_snapshot_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Upgrade snapshot payload to the current schema version.

    Rules:
    - MUST be pure (no providers, no IO)
    - MUST be deterministic
    - MUST be idempotent
    - MUST NOT drop or rewrite unknown fields
    - MUST NOT mutate semantic fingerprint
    """

    if not isinstance(payload, dict):
        raise SnapshotMigrationError("Snapshot payload must be a dict")

    # -----------------------------------------------------------------
    # Work on a shallow copy only
    # -----------------------------------------------------------------
    migrated: Dict[str, Any] = payload.copy()

    # -----------------------------------------------------------------
    # Ensure meta exists, but NEVER overwrite it
    # -----------------------------------------------------------------
    meta = migrated.get("meta")
    if not isinstance(meta, dict):
        meta = {}

    meta = meta.copy()

    version = meta.get("schema_version", 0)

    # -----------------------------------------------------------------
    # Apply migrations incrementally
    # -----------------------------------------------------------------
    if version == 0:
        meta = _migrate_v0_to_v1(meta)
        version = 1

    # -----------------------------------------------------------------
    # Final schema version check
    # -----------------------------------------------------------------
    if version != CURRENT_SNAPSHOT_SCHEMA_VERSION:
        raise SnapshotMigrationError(
            f"Unsupported snapshot schema version: {version}"
        )

    # Explicitly stamp schema version (harmless, non-semantic)
    meta["schema_version"] = CURRENT_SNAPSHOT_SCHEMA_VERSION
    migrated["meta"] = meta

    return migrated


# ---------------------------------------------------------------------
# MIGRATIONS
# ---------------------------------------------------------------------

def _migrate_v0_to_v1(meta: Dict[str, Any]) -> Dict[str, Any]:
    """
    v0 → v1 migration

    v0 characteristics:
    - No schema_version
    - Fingerprint MAY already exist
    """

    migrated = meta.copy()

    # Only introduce schema_version.
    # Fingerprint is semantic — NEVER touch it.
    migrated.setdefault("schema_version", 1)

    return migrated
