from enum import Enum

class RetirementState(str, Enum):
    ACTIVE = "ACTIVE"
    AT_RISK = "AT_RISK"
    COOLING = "COOLING"
    RETIRED = "RETIRED"
    ARCHIVED = "ARCHIVED"


ALLOWED_TRANSITIONS = {
    RetirementState.ACTIVE: {RetirementState.AT_RISK},
    RetirementState.AT_RISK: {RetirementState.COOLING},
    RetirementState.COOLING: {RetirementState.RETIRED},
    RetirementState.RETIRED: {RetirementState.ARCHIVED},
}
