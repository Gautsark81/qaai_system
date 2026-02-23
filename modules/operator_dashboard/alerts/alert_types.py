from enum import Enum


class AlertType(str, Enum):
    # Governance
    GOVERNANCE_PENDING = "governance_pending"
    GOVERNANCE_REJECTED = "governance_rejected"

    # Execution safety
    KILL_SWITCH_ARMED = "kill_switch_armed"
    CANARY_HALTED = "canary_halted"

    # Performance
    SSR_DEGRADATION = "ssr_degradation"
