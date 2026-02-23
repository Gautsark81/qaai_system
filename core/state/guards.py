# core/state/guards.py

from core.state.state_registry import StateRegistry
from core.state.system_state import SystemPhase


def require_phase(min_phase: SystemPhase):
    state = StateRegistry.get()
    if state.phase.value < min_phase.value:
        raise RuntimeError(
            f"System phase {state.phase} < required {min_phase}"
        )


def require_watchlist():
    state = StateRegistry.get()
    if not state.watchlist_loaded:
        raise RuntimeError("Watchlist not loaded")


def require_strategies():
    state = StateRegistry.get()
    if not state.strategies_loaded:
        raise RuntimeError("Strategies not loaded")
