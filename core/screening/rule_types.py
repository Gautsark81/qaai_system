from enum import Enum


class RuleCategory(str, Enum):
    STRUCTURE = "STRUCTURE"
    LIQUIDITY = "LIQUIDITY"
    SANITY = "SANITY"
