# core/strategy/strategy_state.py

from enum import Enum


class StrategyState(Enum):
    CREATED = "CREATED"
    BACKTESTED = "BACKTESTED"
    APPROVED = "APPROVED"
    PAPER = "PAPER"
    LIVE = "LIVE"
    RETIRED = "RETIRED"
    KILLED = "KILLED"
