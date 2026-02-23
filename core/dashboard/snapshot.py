# core/dashboard/snapshot.py

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Tuple, Optional

from core.execution.telemetry_snapshot import ExecutionTelemetrySnapshot


@dataclass(frozen=True)
class CoreSystemSnapshot:
    """
    Canonical, immutable snapshot of the system state *now*.

    - Deterministic
    - Read-only
    - No side effects
    - No computation
    - No external dependencies
    """

    timestamp: datetime
    system_health: str

    screening: Any
    watchlist: Any
    strategies: Any
    capital: Any

    alerts: Tuple[Any, ...]

    # 🔑 Phase 13+ observability (OPTIONAL, READ-ONLY)
    execution_telemetry_snapshot: Optional[ExecutionTelemetrySnapshot] = None
