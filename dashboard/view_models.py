from dataclasses import dataclass
from typing import Tuple, Any
from datetime import datetime


# ======================================================
# Overview
# ======================================================

@dataclass(frozen=True)
class OverviewVM:
    timestamp: datetime
    alert_count: int
    has_screening: bool
    has_watchlist: bool
    has_strategies: bool
    has_capital: bool


# ======================================================
# Screening
# ======================================================

@dataclass(frozen=True)
class ScreeningVM:
    available: bool
    type: str | None = None


# ======================================================
# Watchlist
# ======================================================

@dataclass(frozen=True)
class WatchlistVM:
    available: bool
    count: int | None = None
    type: str | None = None


# ======================================================
# Strategies
# ======================================================

@dataclass(frozen=True)
class StrategiesVM:
    available: bool
    type: str | None = None


# ======================================================
# Meta Alpha
# ======================================================

@dataclass(frozen=True)
class MetaAlphaVM:
    enabled: bool
    total_allocated: float
    allocations: Tuple[Any, ...]


# ======================================================
# Alerts
# ======================================================

@dataclass(frozen=True)
class AlertsVM:
    count: int
    alerts: Tuple[Any, ...]


# ======================================================
# Execution Telemetry (Phase 11.4)
# ======================================================

@dataclass(frozen=True)
class ExecutionEventVM:
    timestamp: datetime
    event_type: str
    message: str


@dataclass(frozen=True)
class ExecutionInvariantVM:
    code: str
    message: str
    detected_at: datetime


@dataclass(frozen=True)
class ExecutionTelemetryVM:
    execution_id: str
    started_at: datetime
    completed_at: datetime | None

    total_orders: int
    filled_orders: int
    rejected_orders: int
    cancelled_orders: int

    events: Tuple[ExecutionEventVM, ...]
    invariant_violations: Tuple[ExecutionInvariantVM, ...]


# ======================================================
# Execution Replay (Phase 12.5)
# ======================================================

@dataclass(frozen=True)
class ReplayResultVM:
    replay_id: str
    execution_id: str
    completed_at: datetime
    invariant_violations: Tuple[str, ...]


@dataclass(frozen=True)
class ReplayDiffItemVM:
    code: str
    message: str


@dataclass(frozen=True)
class ReplayDiffReportVM:
    replay_id: str
    execution_id: str
    compared_at: datetime
    diffs: Tuple[ReplayDiffItemVM, ...]
