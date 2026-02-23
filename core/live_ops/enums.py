from enum import Enum


class TradingMode(str, Enum):
    BACKTEST = "BACKTEST"
    PAPER = "PAPER"
    LIVE = "LIVE"


class StrategyStage(str, Enum):
    GENERATED = "GENERATED"
    PAPER_APPROVED = "PAPER_APPROVED"
    LIVE_APPROVED = "LIVE_APPROVED"
    REJECTED = "REJECTED"


class PromotionDecision(str, Enum):
    PROMOTE = "PROMOTE"
    HOLD = "HOLD"
    REJECT = "REJECT"
