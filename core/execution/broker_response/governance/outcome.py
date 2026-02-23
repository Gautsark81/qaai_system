from enum import Enum


class BrokerOutcome(str, Enum):
    """
    System-level interpretation of a broker response.

    This enum carries NO execution authority.
    """

    SUCCESS = "SUCCESS"
    REJECTED = "REJECTED"
    RETRYABLE_FAILURE = "RETRYABLE_FAILURE"
    TERMINAL_FAILURE = "TERMINAL_FAILURE"
    UNKNOWN = "UNKNOWN"


__all__ = ["BrokerOutcome"]
