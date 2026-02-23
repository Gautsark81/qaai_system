from enum import Enum, auto


class TelemetryCategory(str, Enum):
    MARKET_DATA = "market_data"
    STRATEGY_SIGNAL = "strategy_signal"
    RISK_DECISION = "risk_decision"
    ORDER_LIFECYCLE = "order_lifecycle"
    EXECUTION_FILL = "execution_fill"
    PNL_UPDATE = "pnl_update"
    ERROR = "error"
    HEARTBEAT = "heartbeat"


class TelemetrySeverity(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    CRITICAL = "critical"
