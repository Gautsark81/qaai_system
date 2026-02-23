from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import Enum
from typing import Dict, Mapping

from core.strategy.strategy_state import StrategyState


# ============================
# Strategy Classification Enums
# ============================

class EntryType(Enum):
    """
    High-level strategy entry archetype.
    Used by tournament DNA, redundancy pruning, and diversity filters.
    """
    BREAKOUT = "breakout"
    FADE = "fade"
    MEAN_REVERSION = "mean_reversion"
    TREND_FOLLOWING = "trend_following"
    SCALP = "scalp"


class EfficiencyState(Enum):
    """
    Capital efficiency classification.

    IMPORTANT:
    MEDIUM is REQUIRED for tournament DNA distance and redundancy pruning.
    Do NOT collapse this to binary.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class HoldingPeriod(Enum):
    """
    Expected holding duration of the strategy.
    """
    INTRADAY = "intraday"
    MULTIDAY = "multiday"
    SWING = "swing"
    POSITIONAL = "positional"


# ============================
# Strategy Metadata (Immutable)
# ============================

@dataclass(frozen=True)
class StrategyMetadata:
    """
    Immutable, auditable strategy descriptor.

    This object is SAFE to:
    - persist
    - hash
    - compare
    - replay
    - use inside tournaments

    No runtime mutation is allowed.
    """

    # Identity
    strategy_id: str
    name: str
    version: str

    # Lifecycle
    state: StrategyState
    created_at: str
    last_updated: str

    # Classification (used by tournament & DNA)
    entry_type: EntryType
    efficiency: EfficiencyState
    holding_period: HoldingPeriod

    # Health & diagnostics
    health_metrics: Mapping[str, float] = field(default_factory=dict)
    notes: str = ""

    # ----------------------------
    # State transitions
    # ----------------------------

    def promote(self, new_state: StrategyState) -> "StrategyMetadata":
        """
        Promote strategy to a new lifecycle state.
        """
        return replace(
            self,
            state=new_state,
            last_updated=_utc_now(),
        )

    # ----------------------------
    # Health updates (pure)
    # ----------------------------

    def with_health_metrics(self, metrics: Dict[str, float]) -> "StrategyMetadata":
        """
        Attach updated health metrics (SSR, drawdown, win-rate, etc).
        """
        return replace(
            self,
            health_metrics=dict(metrics),
            last_updated=_utc_now(),
        )

    def with_notes(self, notes: str) -> "StrategyMetadata":
        """
        Attach operator or system notes.
        """
        return replace(
            self,
            notes=notes,
            last_updated=_utc_now(),
        )


# ============================
# Utilities
# ============================

def _utc_now() -> str:
    return datetime.utcnow().isoformat()
