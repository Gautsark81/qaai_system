from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass(frozen=True)
class OversightObservation:
    """
    Canonical oversight signal.

    Properties:
    - Read-only
    - Deterministic
    - Explainable
    - Non-authoritative
    """

    observation_id: str
    category: str                  # CAPITAL | GOVERNANCE | REGIME | STRATEGY | SYSTEM
    severity: str                  # INFO | WARNING | CRITICAL

    summary: str                   # Human-readable headline
    explanation: str               # Why this was emitted

    evidence_refs: List[str]       # decision_ids, checksums, frame_ids
    detected_at: datetime

    # Optional enrichment (never required)
    related_strategy_id: Optional[str] = None
    related_run_id: Optional[str] = None
