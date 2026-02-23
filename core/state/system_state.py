# core/state/system_state.py

from enum import Enum
from dataclasses import dataclass
from datetime import date
from typing import Optional


class SystemPhase(Enum):
    INIT = "INIT"
    DATA_READY = "DATA_READY"
    SCREENED = "SCREENED"
    WATCHLIST_READY = "WATCHLIST_READY"
    STRATEGY_READY = "STRATEGY_READY"
    PAPER = "PAPER"
    LIVE = "LIVE"


@dataclass(frozen=True)
class SystemState:
    trading_day: date
    phase: SystemPhase
    broker_mode: str  # BACKTEST | PAPER | LIVE
    capital_mode: str  # SIM | REAL
    watchlist_loaded: bool
    strategies_loaded: bool

HALTED = "HALTED"
SAFE = "SAFE"
