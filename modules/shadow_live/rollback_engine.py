from datetime import datetime
from modules.shadow_live.shadow_state import ShadowLiveState


class ShadowRollbackEngine:
    def rollback(
        self,
        state: ShadowLiveState,
        reason: str,
    ) -> ShadowLiveState:

        return ShadowLiveState(
            strategy_id=state.strategy_id,
            started_at=state.started_at,
            capital=state.capital,
            peak_pnl=state.peak_pnl,
            current_pnl=state.current_pnl,
            killed_at=datetime.utcnow(),
        )
