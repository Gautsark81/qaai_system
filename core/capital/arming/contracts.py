from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List


class CapitalArmingState(str, Enum):
    DISARMED = "DISARMED"
    SHADOW = "SHADOW"
    PAPER = "PAPER"
    TINY_LIVE = "TINY_LIVE"
    GOVERNED_LIVE = "GOVERNED_LIVE"


@dataclass(frozen=True)
class CapitalArmingDecision:
    """
    Phase 18 — Capital Arming Decision (Immutable Contract)

    This object is:
    - immutable
    - audit-safe
    - replay-safe
    - governance-authoritative
    """

    state: CapitalArmingState
    allowed: bool
    reasons: List[str]
    decided_at: datetime

class CapitalArmingState(str, Enum):
    DISARMED = "DISARMED"
    SHADOW = "SHADOW"
    PAPER = "PAPER"
    TINY_LIVE = "TINY_LIVE"
    GOVERNED_LIVE = "GOVERNED_LIVE"  # ← REQUIRED
    LIVE = "LIVE"    