from enum import Enum


class NSESessionState(str, Enum):
    CLOSED = "CLOSED"
    PRE_OPEN = "PRE_OPEN"
    OPEN = "OPEN"
    NORMAL = "NORMAL"
    SQUARE_OFF_BUFFER = "SQUARE_OFF_BUFFER"
