from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Any


@dataclass
class ScreeningContext:
    """
    LEGACY compatibility wrapper.

    Core screening does NOT use a context object.
    This exists ONLY to satisfy:
    - tests/screening/*
    - screener/jobs.py
    """

    tick_store: Any
    ohlcv_store: Any
    feature_store: Any
    universe: List[str]
    timeframe: str
    as_of: datetime

    @classmethod
    def from_universe(
        cls,
        tick_store,
        ohlcv_store,
        feature_store,
        universe: List[str],
        timeframe: str,
        as_of: datetime,
    ) -> "ScreeningContext":
        return cls(
            tick_store=tick_store,
            ohlcv_store=ohlcv_store,
            feature_store=feature_store,
            universe=universe,
            timeframe=timeframe,
            as_of=as_of,
        )
