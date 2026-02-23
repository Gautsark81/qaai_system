# core/dashboard_read/evidence/record.py

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict

from core.dashboard_read.crypto.snapshot_hash import compute_snapshot_hash
from core.dashboard_read.crypto.chain import (
    compute_chain_hash,
    GENESIS_CHAIN_HASH,
)


EVIDENCE_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class EvidenceRecord:

    snapshot: Dict[str, Any]

    snapshot_hash: str
    previous_chain_hash: str
    chain_hash: str

    schema_version: int = field(default=EVIDENCE_SCHEMA_VERSION)
    producer_id: str = field(default="system")
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @staticmethod
    def create(
        snapshot: Dict[str, Any],
        previous_chain_hash: str = GENESIS_CHAIN_HASH,
        *,
        producer_id: str = "system",
    ) -> "EvidenceRecord":

        snapshot_hash = compute_snapshot_hash(snapshot)

        chain_hash = compute_chain_hash(
            snapshot_hash,
            previous_chain_hash,
        )

        return EvidenceRecord(
            snapshot=snapshot,
            snapshot_hash=snapshot_hash,
            previous_chain_hash=previous_chain_hash,
            chain_hash=chain_hash,
            producer_id=producer_id,
        )