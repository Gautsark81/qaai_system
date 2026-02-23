from enum import Enum

# ======================================================
# Resurrection Trigger Reasons (WHY resurrection started)
# ======================================================

class ResurrectionReason(str, Enum):
    REGIME_SHIFT = "REGIME_SHIFT"
    DATA_EXPANSION = "DATA_EXPANSION"
    EXECUTION_FIX = "EXECUTION_FIX"
    PARAMETER_DRIFT_CORRECTED = "PARAMETER_DRIFT_CORRECTED"
    ALPHA_COMPOSITION_CHANGE = "ALPHA_COMPOSITION_CHANGE"


# ======================================================
# Resurrection Lifecycle States (WHERE in resurrection flow)
# ======================================================

class ResurrectionState(str, Enum):
    RESURRECTION_CANDIDATE = "RESURRECTION_CANDIDATE"
    REVIVAL_SHADOW = "REVIVAL_SHADOW"
    REVIVAL_PAPER = "REVIVAL_PAPER"


# ======================================================
# Resurrection Outcome States (WHAT happened after attempt)
# ======================================================

class OutcomeState(str, Enum):
    """
    Final outcome of a resurrection attempt.

    These states are consumed by:
    - ResurrectionLearningEngine
    - Suppression / cooldown logic
    - Operator dashboards
    """

    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    ABORTED = "ABORTED"   # Governance / operator / safety abort


# ======================================================
# Suppression & Cooldown Governance States
# ======================================================

class SuppressionState(str, Enum):
    """
    Learning-driven suppression state.

    This NEVER mutates lifecycle directly.
    It only gates future resurrection attempts.
    """

    NONE = "NONE"                 # No suppression
    COOLDOWN = "COOLDOWN"         # Temporary block
    PERMANENT_BLOCK = "PERMANENT_BLOCK"  # Hard stop after repeated failures

class SuppressionState(Enum):
    ALLOWED = "allowed"
    SUPPRESSED = "suppressed"