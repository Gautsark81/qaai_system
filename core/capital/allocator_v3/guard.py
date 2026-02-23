from typing import Dict, List

from core.capital.allocator_v3.allocator import CapitalAllocatorV3
from core.capital.allocator_v3.contracts import (
    StrategyCapitalProfile,
    CapitalDecisionArtifact,
)
from core.strategy_factory.fitness.contracts import FitnessResult
from core.regime.taxonomy import MarketRegime
from core.watchlist.models import WatchlistSnapshot
from core.watchlist.errors import WatchlistViolation


class CapitalAllocatorV3Guard:
    """
    HARD GATE before capital allocation.

    Enforces:
    - Watchlist eligibility (symbol-level)
    - Prevents capital, risk, and execution bypass

    This guard is MANDATORY for:
    - shadow live
    - paper trading
    - live trading
    """

    def __init__(self):
        self._allocator = CapitalAllocatorV3()

    def allocate(
        self,
        *,
        profiles: List[StrategyCapitalProfile],
        fitness: Dict[str, FitnessResult],
        regime: MarketRegime,
        signals: Dict[str, object],
        watchlist: WatchlistSnapshot,
    ) -> CapitalDecisionArtifact:

        # ==================================================
        # HARD WATCHLIST ASSERTION (MUST-FIX #1)
        # ==================================================
        for symbol in signals.keys():
            if symbol not in watchlist.entries:
                raise WatchlistViolation(
                    f"Symbol '{symbol}' not in active watchlist"
                )

        # ==================================================
        # PASS THROUGH TO PURE CAPITAL ALLOCATOR
        # ==================================================
        return self._allocator.allocate(
            profiles=profiles,
            fitness=fitness,
            regime=regime,
        )
