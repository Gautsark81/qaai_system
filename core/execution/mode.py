from enum import Enum, auto


class ExecutionMode(Enum):
    """
    Controls how orders are handled.
    """
    SHADOW = auto()   # Send to broker in dry-run / simulated mode
    PAPER = auto()    # Broker paper trading (if supported)
    LIVE = auto()     # Real capital (LOCKED until explicit approval)
