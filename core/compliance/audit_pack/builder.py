# core/compliance/audit_pack/builder.py

from core.capital.usage_ledger.ledger import CapitalUsageLedger

from .models import AuditArtifact, AuditPack
from .manifest import build_manifest
from .checksum import compute_checksum


class AuditPackBuilder:
    """
    READ-ONLY compliance aggregator.

    HARD GUARANTEES:
    - No execution
    - No mutation
    - No runtime entropy (NO time, NO counters, NO UUIDs)
    - No static singletons
    - Deterministic output (byte-for-byte)
    """

    def build(self) -> AuditPack:
        artifacts = []

        # ------------------------------------------------------------------
        # SEBI Trade Export
        # ------------------------------------------------------------------
        # Phase 28.1: SEBITradeExport is a PER-TRADE RECORD.
        # Audit Pack carries a deterministic COLLECTION.
        # Empty list is regulator-valid.
        # ------------------------------------------------------------------
        artifacts.append(
            AuditArtifact(
                kind="SEBI_TRADE_EXPORT",
                payload=[],
            )
        )

        # ------------------------------------------------------------------
        # Capital Usage Ledger (IMMUTABLE SNAPSHOT)
        # ------------------------------------------------------------------
        # Ledger.entries() is already deterministic & append-only
        # ------------------------------------------------------------------
        ledger = CapitalUsageLedger()
        artifacts.append(
            AuditArtifact(
                kind="CAPITAL_USAGE_LEDGER",
                payload=ledger.entries(),
            )
        )

        # ------------------------------------------------------------------
        # Governance Decisions (DESCRIPTIVE ONLY)
        # ------------------------------------------------------------------
        # CRITICAL FIX:
        # - Removed datetime.utcnow()
        # - Audit packs MUST be replay-safe
        # - Time belongs in lifecycle/event logs, NOT audit snapshots
        # ------------------------------------------------------------------
        artifacts.append(
            AuditArtifact(
                kind="GOVERNANCE_DECISIONS",
                payload={
                    "source": "governance",
                    "note": "decisions are externally persisted; audit pack is a snapshot",
                },
            )
        )

        # ------------------------------------------------------------------
        # Lifecycle Events
        # ------------------------------------------------------------------
        # Lifecycle events are already persisted elsewhere.
        # Audit Pack carries a deterministic collection only.
        # ------------------------------------------------------------------
        artifacts.append(
            AuditArtifact(
                kind="LIFECYCLE_EVENTS",
                payload=[],
            )
        )

        # ------------------------------------------------------------------
        # Deterministic ordering (CRITICAL)
        # ------------------------------------------------------------------
        artifacts = sorted(
            artifacts,
            key=lambda a: a.kind,
        )

        # ------------------------------------------------------------------
        # Deterministic Manifest
        # ------------------------------------------------------------------
        manifest = build_manifest(artifacts)

        # ------------------------------------------------------------------
        # Deterministic Checksum (FINAL)
        # ------------------------------------------------------------------
        provisional = AuditPack(
            manifest=manifest,
            artifacts=artifacts,
            checksum="",
        )

        checksum = compute_checksum(provisional.serialize())

        return AuditPack(
            manifest=manifest,
            artifacts=artifacts,
            checksum=checksum,
        )
