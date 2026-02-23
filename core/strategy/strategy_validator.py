# core/strategy/strategy_validator.py

from core.state.guards import require_watchlist
from core.state.state_registry import StateRegistry
from core.state.system_state import SystemPhase
from core.strategy.strategy_metadata import StrategyMetadata
from core.strategy.strategy_state import StrategyState


class StrategyValidator:
    """
    Enforces lifecycle + system rules before execution.
    """

    @staticmethod
    def validate_for_execution(meta: StrategyMetadata):
        state = StateRegistry.get()

        if state.phase.value < SystemPhase.STRATEGY_READY.value:
            raise RuntimeError("System not ready for strategies")

        require_watchlist()

        if meta.state not in (StrategyState.PAPER, StrategyState.LIVE):
            raise RuntimeError(
                f"Strategy {meta.strategy_id} not executable (state={meta.state})"
            )
