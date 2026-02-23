from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CapitalThrottleDecision:
    """
    Result of capital throttling / cooldown evaluation.
    """

    allowed: bool
    reason: str
    retry_after_seconds: Optional[int]

    def __post_init__(self) -> None:
        if not isinstance(self.allowed, bool):
            raise TypeError("allowed must be a boolean")

        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string")

        if self.retry_after_seconds is not None:
            if self.retry_after_seconds <= 0:
                raise ValueError("retry_after_seconds must be positive")
