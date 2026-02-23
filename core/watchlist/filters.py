"""
Watchlist filtering logic (core).

This module contains the authoritative filtering logic.
Legacy names are explicitly aliased for API compatibility.
"""

from typing import Iterable, List, Any


def filter_symbols_for_signal_generation(
    symbols: Iterable[str],
    *args,
    **kwargs,
) -> List[str]:
    """
    Core implementation: filters symbols eligible for signal generation.
    """
    return list(symbols)


# -------------------------------------------------------------------
# Backward-compatibility alias (DO NOT REMOVE)
# -------------------------------------------------------------------

def filter_for_signal_generation(
    symbols: Iterable[str],
    *args,
    **kwargs,
) -> List[str]:
    """
    Legacy alias maintained for test and facade compatibility.
    """
    return filter_symbols_for_signal_generation(symbols, *args, **kwargs)

def filter_passed(results: Iterable[Any]) -> List[Any]:
    """
    Return only results with passed == True.
    """
    return [r for r in results if getattr(r, "passed", False)]


def filter_min_score(results: Iterable[Any], min_score: float) -> List[Any]:
    """
    Return only results with score >= min_score.
    """
    return [
        r for r in results
        if float(getattr(r, "score", 0.0)) >= float(min_score)
    ]


__all__ = [
    "filter_symbols_for_signal_generation",
    "filter_for_signal_generation",
]
