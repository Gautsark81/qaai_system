"""
Pre-trade risk filters.

RiskConfig: simple container for policy.
check_risk_gates: returns (passed:bool, reason:str)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
import datetime as dt

import pandas as pd

@dataclass
class RiskConfig:
    max_position_per_symbol: float = 0.1    # fraction of portfolio capital
    max_exposure_total: float = 0.4         # fraction of portfolio capital
    trade_start_hour: int = 9               # local exchange hour (24h)
    trade_end_hour: int = 15
    allow_weekends: bool = False
    require_regime_low_vol: bool = False    # sample regime gating flag


def check_risk_gates(cfg: RiskConfig, symbol: str, proposed_size: float, features: Optional[pd.Series] = None) -> Tuple[bool, str]:
    """
    Evaluate simple risk gates.
    - proposed_size: fraction (0..1) of capital
    - features: optional feature row (may include regime flags)
    Returns: (passed, reason)
    """
    if proposed_size <= 0:
        return False, "zero_size"

    if features is not None:
        # regime gating
        if cfg.require_regime_low_vol:
            if float(features.get("volatility_regime_high", 0)) == 1:
                return False, "regime_high_vol"

    # time gating (use current time)
    now = dt.datetime.utcnow()
    # map to naive hour; user can adjust to exchange timezone in calling code
    hour = now.hour
    weekday = now.weekday()
    if not cfg.allow_weekends and weekday >= 5:
        return False, "weekend_block"

    if hour < cfg.trade_start_hour or hour >= cfg.trade_end_hour:
        return False, "outside_hours"

    if proposed_size > cfg.max_position_per_symbol:
        return False, "size_exceeds_symbol_limit"

    # NOTE: total exposure checks require portfolio state; caller must enforce separately
    return True, "ok"
