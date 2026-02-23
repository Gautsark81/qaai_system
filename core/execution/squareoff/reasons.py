from enum import Enum


class SquareOffReason(str, Enum):
    """
    Canonical reasons for forced square-off.

    These reasons are GOVERNANCE-LEVEL and immutable.
    """
    KILL_SWITCH = "KILL_SWITCH"
    MARKET_CLOSE = "MARKET_CLOSE"
    RISK_VIOLATION = "RISK_VIOLATION"
    BROKER_FAILURE = "BROKER_FAILURE"
