from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class LiveApprovalRecord:
    """
    Human approval required for live trading.
    """
    strategy_id: str
    approved_by: str
    approved_at: datetime
    expires_at: datetime
    notes: str


@dataclass(frozen=True)
class LiveGateDecision:
    """
    Final machine decision before live execution.
    """
    strategy_id: str
    allowed: bool
    reasons: List[str]
    evaluated_at: datetime
