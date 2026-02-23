from enum import Enum


class KillScope(str, Enum):
    GLOBAL = "global"
    STRATEGY = "strategy"
    SYMBOL = "symbol"
