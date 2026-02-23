from enum import Enum


class IncidentType(str, Enum):
    """
    Canonical incident taxonomy.

    This enum answers:
    - what category failed
    - not why
    - not how to fix
    """

    DATA_INTEGRITY = "DATA_INTEGRITY"
    EXECUTION_INVARIANT = "EXECUTION_INVARIANT"
    CAPITAL_BREACH = "CAPITAL_BREACH"
    GOVERNANCE_VIOLATION = "GOVERNANCE_VIOLATION"
    OPERATOR_ABSENCE = "OPERATOR_ABSENCE"
    EXTERNAL_DEPENDENCY = "EXTERNAL_DEPENDENCY"
