"""
Singular alias for ScreeningResult.

This file exists to support imports like:
    from screening.result import ScreeningResult

Canonical implementation lives in screening.results
"""

from screening.results import ScreeningResult

__all__ = ["ScreeningResult"]

