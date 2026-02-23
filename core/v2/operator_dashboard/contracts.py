from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class StrategyStatus:
    strategy_id: str
    lifecycle_state: str
    shadow_pnl: float
    last_updated: datetime


@dataclass(frozen=True)
class ApprovalStatus:
    strategy_id: str
    approved: bool
    approved_by: Optional[str]
    expires_at: Optional[datetime]


@dataclass(frozen=True)
class SafetyStatus:
    strategy_id: str
    live_allowed: bool
    last_check: datetime
    reason_summary: str
