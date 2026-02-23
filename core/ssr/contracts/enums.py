from enum import Enum


class SSRStatus(str, Enum):
    STRONG = "STRONG"
    STABLE = "STABLE"
    WEAK = "WEAK"
    FAILING = "FAILING"
