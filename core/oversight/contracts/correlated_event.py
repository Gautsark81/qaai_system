# core/oversight/contracts/correlated_event.py

from dataclasses import dataclass
from datetime import datetime
from typing import FrozenSet, Tuple


@dataclass(frozen=True)
class CorrelatedOversightEvent:
    """
    Immutable correlated oversight signal.

    Emitted when multiple oversight detectors
    jointly indicate elevated system risk.

    ❌ No execution authority
    ❌ No governance power
    ❌ No mutation rights
    """

    # --- Identity ---
    event_id: str
    generated_at: datetime

    # --- Severity ---
    severity: str               # INFO | WARNING | CRITICAL

    # --- Correlation context ---
    involved_domains: FrozenSet[str]     # capital, governance, lifecycle, regime
    detectors: FrozenSet[str]            # detector class names

    # --- Human-readable explanation ---
    summary: str
    contributing_findings: Tuple[str, ...]

    # --- Evidence linkage ---
    evidence_ids: Tuple[str, ...]

    # --- Safety metadata ---
    requires_human_attention: bool
