# core/dashboard_read/persistence/store.py

from __future__ import annotations

import json
from pathlib import Path
from typing import Union

from core.dashboard_read.evidence.record import EvidenceRecord


class PersistenceError(Exception):
    """Raised when persistence contract is violated."""


def store_evidence_record(
    record: EvidenceRecord,
    path: Union[str, Path],
) -> None:
    """
    Persist an EvidenceRecord to disk.

    Rules:
    - Only EvidenceRecord is accepted
    - JSON-safe serialization
    """

    if not isinstance(record, EvidenceRecord):
        raise PersistenceError("Only EvidenceRecord may be persisted")

    path = Path(path)

    data = {
        "snapshot": record.snapshot,
        "snapshot_hash": record.snapshot_hash,
        "previous_chain_hash": record.previous_chain_hash,
        "chain_hash": record.chain_hash,
        "schema_version": record.schema_version,
        "producer_id": record.producer_id,
        "created_at": record.created_at,
    }

    try:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as exc:
        raise PersistenceError(f"Failed to persist evidence: {exc}") from exc
