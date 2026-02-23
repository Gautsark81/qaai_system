from dataclasses import dataclass
from datetime import datetime

from .models import InstitutionalMemory


@dataclass(frozen=True)
class InstitutionalMemorySnapshot:
    """
    Immutable institutional memory snapshot.
    """
    memory: InstitutionalMemory
    generated_at: datetime
    snapshot_version: str
