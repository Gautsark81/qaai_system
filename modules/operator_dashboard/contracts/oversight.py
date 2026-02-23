# modules/operator_dashboard/contracts/oversight.py

from dataclasses import dataclass
from datetime import datetime
from typing import FrozenSet, Optional


@dataclass(frozen=True)
class OversightEventSnapshot:
    """
    Read-only snapshot of an oversight finding/event
    surfaced to the operator dashboard.
    """

    timestamp: datetime

    detector: str
    severity: str              # INFO | WARNING | CRITICAL

    entity_type: str           # STRATEGY | CAPITAL | SYSTEM
    entity_id: Optional[str]

    message: str

    evidence_checksum: Optional[str]

    # Which detectors contributed to this surfaced event
    detectors: FrozenSet[str]
