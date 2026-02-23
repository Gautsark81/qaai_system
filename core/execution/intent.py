from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionIntent:
    """
    Canonical execution intent shared by PAPER and LIVE engines.

    Laws:
    - Immutable
    - Hashable
    - Replayable
    - Venue-agnostic
    - No execution logic
    """

    symbol: str
    side: str
    quantity: int
    price: float
    venue: str
