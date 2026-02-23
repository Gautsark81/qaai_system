# core/dashboard_read/persistence/load.py

from __future__ import annotations

import json
from pathlib import Path
from typing import Union

from core.dashboard_read.evidence.record import EvidenceRecord
from core.dashboard_read.verification.verifier import verify_evidence_record
from core.dashboard_read.persistence.store import PersistenceError


def load_evidence_record(
    path: Union[str, Path],
) -> EvidenceRecord:
    """
    Load and verify an EvidenceRecord from disk.

    Rules:
    - Evidence must verify before returning
    - Corruption fails fast
    """

    path = Path(path)

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise PersistenceError(f"Failed to load evidence: {exc}") from exc

    record = EvidenceRecord(
        snapshot=raw["snapshot"],
        snapshot_hash=raw["snapshot_hash"],
        previous_chain_hash=raw["previous_chain_hash"],
        chain_hash=raw["chain_hash"],
        schema_version=raw["schema_version"],
        producer_id=raw["producer_id"],
        created_at=raw["created_at"],
    )

    report = verify_evidence_record(record)
    if not report.is_valid:
        raise PersistenceError(
            f"Evidence verification failed: {[i.code for i in report.issues]}"
        )

    return record
