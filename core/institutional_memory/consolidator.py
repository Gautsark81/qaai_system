import hashlib
import json
from datetime import datetime
from typing import Iterable, Tuple

from .models import InstitutionalMemory, InstitutionalMemoryRecord
from .snapshot import InstitutionalMemorySnapshot


def _freeze(items: Iterable[InstitutionalMemoryRecord]) -> Tuple[InstitutionalMemoryRecord, ...]:
    return tuple(items)


def _version_key(records: Tuple[InstitutionalMemoryRecord, ...]) -> str:
    payload = tuple(
        map(
            lambda r: (r.category, repr(r.payload)),
            records,
        )
    )
    return hashlib.sha256(json.dumps(payload).encode()).hexdigest()


def build_institutional_memory_snapshot(
    records: Iterable[InstitutionalMemoryRecord],
) -> InstitutionalMemorySnapshot:
    """
    Deterministic, read-only institutional memory consolidator.

    Guarantees:
    - No execution authority
    - No mutation
    - No loops
    - Replayable snapshot
    """

    frozen = _freeze(records)

    memory = InstitutionalMemory(
        records=frozen,
        checksum=_version_key(frozen),
    )

    return InstitutionalMemorySnapshot(
        memory=memory,
        generated_at=datetime.utcnow(),
        snapshot_version=memory.checksum,
    )
