# path: qaai_system/portfolio/portfolio_state.py
from __future__ import annotations

"""
PortfolioState — thin wrapper over PortfolioSnapshot for higher-level usage.

This matches the Phase 4 design:
- cash, equity, positions, closed_trades (via tracker), daily PnL, exposures
- exposes .as_dict() and .from_tracker(...) helpers
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional

from portfolio.models import PortfolioSnapshot
from .position_tracker import PositionTracker


@dataclass
class PortfolioState:
    """
    Higher-level portfolio view used by orchestrator / monitoring / dashboards.

    Internally wraps a PortfolioSnapshot but gives a stable API surface.
    """

    snapshot: PortfolioSnapshot

    @property
    def timestamp(self) -> float:
        return self.snapshot.timestamp

    @property
    def equity(self) -> Optional[float]:
        return self.snapshot.equity

    @property
    def cash(self) -> Optional[float]:
        return self.snapshot.cash

    @property
    def realized_pnl(self) -> float:
        return self.snapshot.realized_pnl

    @property
    def unrealized_pnl(self) -> float:
        return self.snapshot.unrealized_pnl

    @property
    def gross_exposure(self) -> float:
        return self.snapshot.gross_exposure

    @property
    def net_exposure(self) -> float:
        return self.snapshot.net_exposure

    @property
    def num_open_positions(self) -> int:
        return self.snapshot.num_open_positions

    @property
    def positions(self) -> Dict[str, Dict[str, Any]]:
        return self.snapshot.positions

    def as_dict(self) -> Dict[str, Any]:
        """
        Flatten to a dict, suitable for JSON logs / monitoring.
        """
        return self.snapshot.as_dict()

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------
    @classmethod
    def from_snapshot(cls, snapshot: PortfolioSnapshot) -> "PortfolioState":
        return cls(snapshot=snapshot)

    @classmethod
    def from_tracker(
        cls,
        tracker: PositionTracker,
        equity: Optional[float] = None,
        cash: Optional[float] = None,
    ) -> "PortfolioState":
        """
        Build a PortfolioState directly from a PositionTracker instance.
        """
        snap = tracker.get_portfolio_snapshot(equity=equity, cash=cash)
        return cls(snapshot=snap)
