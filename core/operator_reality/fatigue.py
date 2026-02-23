from dataclasses import dataclass


@dataclass(frozen=True)
class OperatorFatiguePolicy:
    """
    Defines operator fatigue limits.

    All time values are deterministic and externally supplied.
    This policy does NOT read clocks or system time.
    """

    max_active_seconds: int
    warning_threshold_seconds: int

    def is_expired(self, *, intent_timestamp: int, now_timestamp: int) -> bool:
        if now_timestamp < intent_timestamp:
            raise ValueError("now_timestamp cannot be earlier than intent_timestamp")

        return (now_timestamp - intent_timestamp) >= self.max_active_seconds

    def is_warning(self, *, intent_timestamp: int, now_timestamp: int) -> bool:
        if now_timestamp < intent_timestamp:
            raise ValueError("now_timestamp cannot be earlier than intent_timestamp")

        return (now_timestamp - intent_timestamp) >= self.warning_threshold_seconds
