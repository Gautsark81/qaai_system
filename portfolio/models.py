# path: qaai_system/portfolio/models.py
from __future__ import annotations

"""
Portfolio models: Position & PortfolioSnapshot.

These are generic, broker-agnostic dataclasses used by PositionTracker and
higher-level reporting / monitoring code.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional
import time


@dataclass
class Position:
    """
    Represents an aggregated position in a single symbol.

    - Handles both long and short (side = 'LONG' / 'SHORT').
    - Tracks realized & unrealized PnL separately.
    """

    symbol: str
    side: str  # 'LONG' or 'SHORT'
    quantity: int
    avg_price: float

    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    fees: float = 0.0

    first_open_ts: float = field(default_factory=lambda: time.time())
    last_update_ts: float = field(default_factory=lambda: time.time())

    meta: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


@dataclass
class PortfolioSnapshot:
    """
    A point-in-time view of the portfolio.

    - equity / cash are optional; can be filled from broker or risk engine.
    """

    timestamp: float
    equity: Optional[float] = None
    cash: Optional[float] = None

    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0

    gross_exposure: float = 0.0
    net_exposure: float = 0.0

    num_open_positions: int = 0

    positions: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "equity": self.equity,
            "cash": self.cash,
            "realized_pnl": self.realized_pnl,
            "unrealized_pnl": self.unrealized_pnl,
            "gross_exposure": self.gross_exposure,
            "net_exposure": self.net_exposure,
            "num_open_positions": self.num_open_positions,
            "positions": self.positions,
        }
