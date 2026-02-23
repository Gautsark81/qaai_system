from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CapitalEligibilityDecision:
    """
    Immutable governance decision indicating whether a strategy
    is eligible to receive capital.
    """

    eligible: bool
    reason: str
