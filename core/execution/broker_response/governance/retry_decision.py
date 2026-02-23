from enum import Enum


class RetryDecision(str, Enum):
    RETRYABLE = "RETRYABLE"
    NON_RETRYABLE = "NON_RETRYABLE"


__all__ = ["RetryDecision"]
