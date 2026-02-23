from dataclasses import dataclass, field
from datetime import datetime
from typing import Tuple, Any

from modules.operator_dashboard.contracts.oversight import (
    OversightEventSnapshot,
)


@dataclass(frozen=True)
class DashboardSnapshot:
    """
    Canonical, immutable dashboard snapshot.

    Phase-F GOVERNANCE CONTRACT.
    This shape is READ-ONLY and MUST remain stable.
    """

    # ------------------------------------------------------------------
    # Core
    # ------------------------------------------------------------------
    timestamp: datetime

    # ------------------------------------------------------------------
    # System surfaces
    # ------------------------------------------------------------------
    system: Any
    capital: Any

    # ------------------------------------------------------------------
    # Strategy & alert surfaces
    # ------------------------------------------------------------------
    strategies: Tuple[Any, ...] = field(default_factory=tuple)
    alerts: Tuple[Any, ...] = field(default_factory=tuple)

    # ------------------------------------------------------------------
    # Optional / future-safe surfaces
    # (MUST exist, may be empty)
    # ------------------------------------------------------------------
    regime: Any = field(default_factory=dict)
    explainability: Any = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Oversight (MANDATORY, read-only)
    # ------------------------------------------------------------------
    oversight_events: Tuple[OversightEventSnapshot, ...] = field(
        default_factory=tuple
    )
