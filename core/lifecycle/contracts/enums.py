from enum import Enum


class LifecycleState(str, Enum):
    """
    Canonical lifecycle states exposed as a public contract.

    This enum is the ONLY lifecycle state reference allowed for:
    - observability
    - operator dashboards
    - alerts
    - governance views
    """

    CANDIDATE = "CANDIDATE"
    PAPER = "PAPER"
    LIVE = "LIVE"
    PAUSED = "PAUSED"
    RETIRED = "RETIRED"
    KILLED = "KILLED"


class TransitionReason(str, Enum):
    # =====================================================
    # SSR-DRIVEN TRANSITIONS
    # =====================================================
    SSR_STRONG = "SSR_STRONG"
    SSR_WEAK = "SSR_WEAK"
    SSR_FAILING = "SSR_FAILING"

    # =====================================================
    # HEALTH-DRIVEN TRANSITIONS
    # =====================================================
    HEALTH_DEGRADED = "HEALTH_DEGRADED"
    HEALTH_CRITICAL = "HEALTH_CRITICAL"

    # =====================================================
    # EXECUTION / CAPITAL GOVERNANCE
    # =====================================================
    EXECUTION_QUALITY = "EXECUTION_QUALITY"
    EXECUTION_BREACH = "EXECUTION_BREACH"

    # =====================================================
    # TIME / OPERATOR
    # =====================================================
    TIME_IN_STATE = "TIME_IN_STATE"
    OPERATOR_OVERRIDE = "OPERATOR_OVERRIDE"
