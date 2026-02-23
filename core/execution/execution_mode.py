from __future__ import annotations

from enum import Enum


class ExecutionMode(str, Enum):
    """
    Execution mode selector.

    SHADOW:
    - Deterministic execution intent
    - No broker interaction
    - No capital mutation

    PAPER:
    - Virtual execution
    - Virtual capital mutation only
    - No real broker interaction
    """

    SHADOW = "shadow"
    PAPER = "paper"
