# path: qaai_system/risk/risk_limits.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class RiskLimits:
    """
    Configuration for portfolio and order-level risk limits.

    All fields are optional; None means "limit disabled".

    Fields
    ------
    max_daily_loss : float, optional
        Hard daily loss limit in absolute currency.
    max_daily_loss_pct : float, optional
        Hard daily loss as a fraction of equity (e.g. 0.02 for 2%).

    max_intraday_drawdown_pct : float, optional
        Maximum intraday equity drawdown from start-of-day equity.
        For example, 0.05 means -5% from start_of_day_equity.

    max_order_notional_pct : float, optional
        Maximum notional per order as a fraction of equity.
    max_order_notional_value : float, optional
        Maximum notional per order in absolute currency.

    max_symbol_weight : float, optional
        Maximum symbol exposure / equity.
    max_gross_exposure_pct : float, optional
        Maximum gross exposure / equity.
    max_net_exposure_pct : float, optional
        Maximum |net_exposure| / equity.

    max_open_positions : int, optional
        Maximum number of distinct symbols with non-zero position.

    max_strategy_daily_loss : dict[str, float]
        Per-strategy absolute daily loss limit. Key = strategy_id.
    max_strategy_daily_loss_pct : dict[str, float]
        Per-strategy daily loss as a fraction of equity. Key = strategy_id.
    """

    # Daily loss limits (global)
    max_daily_loss: Optional[float] = None
    max_daily_loss_pct: Optional[float] = None

    # Intraday drawdown
    max_intraday_drawdown_pct: Optional[float] = None

    # Per-order risk
    max_order_notional_pct: Optional[float] = None
    max_order_notional_value: Optional[float] = None

    # Portfolio-level risk
    max_symbol_weight: Optional[float] = None
    max_gross_exposure_pct: Optional[float] = None
    max_net_exposure_pct: Optional[float] = None

    # Position count
    max_open_positions: Optional[int] = None

    # Strategy-specific daily loss
    max_strategy_daily_loss: Dict[str, float] = field(default_factory=dict)
    max_strategy_daily_loss_pct: Dict[str, float] = field(default_factory=dict)
