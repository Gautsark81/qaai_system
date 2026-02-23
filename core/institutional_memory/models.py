from dataclasses import dataclass
from typing import Any, Dict, Tuple


@dataclass(frozen=True)
class InstitutionalMemoryRecord:
    """
    Immutable consolidated institutional memory record.
    """
    category: str
    payload: Any


@dataclass(frozen=True)
class InstitutionalMemory:
    """
    Governance-grade institutional memory surface.
    """
    records: Tuple[InstitutionalMemoryRecord, ...]
    checksum: str
