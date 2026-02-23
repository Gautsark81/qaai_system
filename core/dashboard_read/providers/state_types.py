from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass(frozen=True)
class CapitalState:
    total_capital: float
    allocated_capital: float
    free_capital: float
    utilization_ratio: float
    throttle_active: bool


@dataclass(frozen=True)
class ComplianceState:
    audit_packs_generated: int
    last_audit_timestamp: str
    violations_detected: int
    regulator_exports_ready: bool


@dataclass(frozen=True)
class ExecutionPosition:
    symbol: str
    quantity: int
    exposure: float
    stop_loss: float


@dataclass(frozen=True)
class ExecutionState:
    intents_created: int
    intents_blocked: int
    blocked_reasons: Dict[str, int]
    positions: List[ExecutionPosition]
    fills: int


@dataclass(frozen=True)
class IncidentState:
    open_incidents: int
    total_incidents: int
    last_incident_type: str
    capital_frozen: bool


@dataclass(frozen=True)
class MarketState:
    volatility: str
    liquidity: str
    stress_level: str
    extreme_active: bool
    extreme_classification: str
    session: str


@dataclass(frozen=True)
class OpsState:
    uptime_seconds: int
    restart_count: int
    degraded_services: List[str]
    last_error: str


@dataclass(frozen=True)
class PaperState:
    enabled: bool
    trades_executed: int
    pnl: float
    win_rate: float
    drawdown: float


@dataclass(frozen=True)
class ScreeningState:
    symbols_seen: int
    passed: int
    rejected_by_reason: Dict[str, int]


@dataclass(frozen=True)
class RiskState:
    checks_passed: int
    checks_failed: int
    dominant_violation: str
    freeze_active: bool


@dataclass(frozen=True)
class ShadowState:
    enabled: bool
    decisions_mirrored: int
    divergences_detected: int
    last_divergence_reason: str


@dataclass(frozen=True)
class StrategySnapshot:
    strategy_id: str
    age_days: int
    health_score: float
    drawdown: float
    trailing_sl: float
    status: str


@dataclass(frozen=True)
class StrategyState:
    strategies: List[StrategySnapshot]


@dataclass(frozen=True)
class PipelineState:
    screening_symbols_seen: int
    screening_passed: int
    screening_rejected: Dict[str, int]
    watchlist_added: int
    watchlist_removed: int
    watchlist_active: int
    strategies_generated: int
    strategies_active: int
    strategies_retired: int


@dataclass(frozen=True)
class SystemHealthState:
    data_feeds: List[str]
    degraded_services: List[str]