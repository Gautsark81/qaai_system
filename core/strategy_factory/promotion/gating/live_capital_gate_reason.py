from enum import Enum


class LiveCapitalGateReason(Enum):
    SSR_BELOW_THRESHOLD = "ssr_below_threshold"
    RISK_ENVELOPE_VIOLATION = "risk_envelope_violation"
    INVALID_PROMOTION_STATE = "invalid_promotion_state"
