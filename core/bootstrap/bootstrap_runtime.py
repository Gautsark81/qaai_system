# core/bootstrap/bootstrap_runtime.py

from core.state.state_registry import StateRegistry
from core.state.system_state import SystemPhase
from core.watchlist.watchlist_loader import WatchlistLoader


def bootstrap_runtime():
    # INIT
    StateRegistry.initialize()

    # Load watchlist
    WatchlistLoader().load()
    StateRegistry.transition(
        phase=SystemPhase.WATCHLIST_READY,
        watchlist_loaded=True,
    )

    # Strategies will be loaded later
    StateRegistry.transition(
        phase=SystemPhase.STRATEGY_READY,
        strategies_loaded=True,
    )
