from enum import Enum


class RuntimeMode(str, Enum):
    LIVE = "live"
    SIM = "sim"
    BACKTEST = "backtest"
