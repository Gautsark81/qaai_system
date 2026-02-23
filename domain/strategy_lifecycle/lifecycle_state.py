from enum import Enum


class StrategyLifecycleState(str, Enum):
    CREATED = "CREATED"
    BACKTEST = "BACKTEST"
    PAPER = "PAPER"
    LIVE_CANDIDATE = "LIVE_CANDIDATE"
    LIVE = "LIVE"
    DEGRADED = "DEGRADED"
    PAUSED = "PAUSED"
    RETIRED = "RETIRED"
