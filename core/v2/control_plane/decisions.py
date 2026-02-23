from enum import Enum


class PromotionDecision(str, Enum):
    PROMOTE = "PROMOTE"
    HOLD = "HOLD"
    PAUSE = "PAUSE"
    KILL = "KILL"
