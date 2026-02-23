from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict


@dataclass(frozen=True)
class AuditEvidence:
    """
    Canonical audit evidence for forced square-off.
    """

    audit_id: str
    reason: str
    positions: Dict[str, int]
    created_at: datetime = datetime.utcnow()
