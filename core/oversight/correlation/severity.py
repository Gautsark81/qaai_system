"""
Canonical severity definitions for Oversight.

This file is the SINGLE source of truth for severity semantics.
"""

from enum import Enum


class SeverityLevel(str, Enum):
    """
    Oversight severity levels.

    Ordering (low → high):
    INFO < WARNING < CRITICAL
    """

    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
