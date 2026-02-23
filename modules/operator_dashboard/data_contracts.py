from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime


# ================= Strategy =================

@dataclass(frozen=True)
class StrategyLifecycleDTO:
    strategy_id: str
    stage: str
    updated_at: datetime


@dataclass(frozen=True)
class ApprovalStatusDTO:
    strategy_id: str
    approved: bool
    approver: Optional[str]
    expires_at: Optional[datetime]
    reason: Optional[str]


@dataclass(frozen=True)
class StrategySummaryDTO:
    strategy_id: str
    name: str
    status: str
    ssr: float
    total_trades: int
    win_rate: float
    pnl: float
    max_drawdown: float
    risk_score: float
    last_signal_ts: Optional[str]


# ================= System =================

@dataclass(frozen=True)
class SystemHealthDTO:
    trading_mode: str
    kill_switch: bool
    broker_connected: bool
    capital_utilization_pct: float
    system_status: str
    components: Dict[str, str]
    last_heartbeat_ts: str


@dataclass(frozen=True)
class AlertDTO:
    level: str
    source: str
    message: str
    timestamp: str


@dataclass(frozen=True)
class CapitalStateDTO:
    total_capital: float
    deployed_capital: float
    available_capital: float
    max_daily_drawdown: float


# ================= Dashboard =================

@dataclass(frozen=True)
class DashboardStateDTO:
    system: SystemHealthDTO
    strategies: List[StrategySummaryDTO]
    alerts: List[AlertDTO]
    capital: CapitalStateDTO

    # REQUIRED by test_state_assembler_module.py
    timestamp: str
