# core/state/state_registry.py

from datetime import date
from core.state.system_state import SystemState, SystemPhase


class StateRegistry:
    """
    Read-mostly global state registry.
    """

    _state: SystemState | None = None

    @classmethod
    def initialize(cls):
        if cls._state is not None:
            return

        cls._state = SystemState(
            trading_day=date.today(),
            phase=SystemPhase.INIT,
            broker_mode="BACKTEST",
            capital_mode="SIM",
            watchlist_loaded=False,
            strategies_loaded=False,
        )

    @classmethod
    def get(cls) -> SystemState:
        if cls._state is None:
            raise RuntimeError("SystemState not initialized")
        return cls._state

    @classmethod
    def transition(
        cls,
        phase: SystemPhase,
        watchlist_loaded: bool | None = None,
        strategies_loaded: bool | None = None,
        broker_mode: str | None = None,
        capital_mode: str | None = None,
    ):
        if cls._state is None:
            raise RuntimeError("SystemState not initialized")

        cls._state = SystemState(
            trading_day=cls._state.trading_day,
            phase=phase,
            broker_mode=broker_mode or cls._state.broker_mode,
            capital_mode=capital_mode or cls._state.capital_mode,
            watchlist_loaded=(
                watchlist_loaded
                if watchlist_loaded is not None
                else cls._state.watchlist_loaded
            ),
            strategies_loaded=(
                strategies_loaded
                if strategies_loaded is not None
                else cls._state.strategies_loaded
            ),
        )
