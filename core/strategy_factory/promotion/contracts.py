from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class PromotionDecision:
    """
    Phase 17 Promotion Decision Contract

    This is the authoritative, test-defined contract used by:
    - Lifecycle state machine
    - Promotion governance
    - Audit & replay systems

    NOTE:
    This is intentionally decoupled from promotion.engine
    to preserve contract stability.
    """

    strategy_dna: str
    promoted: bool
    sizing_fraction: float
    reasons: List[str]
    decided_at: datetime
