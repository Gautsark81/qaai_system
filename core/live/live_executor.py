# core/live/live_executor.py

from core.state.guards import require_phase
from core.state.system_state import SystemPhase
from core.live.live_approval import LiveApproval
from core.live.live_capital_guard import LiveCapitalGuard
from core.live.live_kill_switch import LiveKillSwitch


class LiveExecutor:
    """
    Executes LIVE trades with full governance.
    """

    def __init__(self, capital_guard: LiveCapitalGuard):
        self.approval = LiveApproval()
        self.capital_guard = capital_guard
        self.kill_switch = LiveKillSwitch()

    def execute(
        self,
        strategy_meta,
        symbol: str,
        side: str,
        quantity: int,
        price: float,
    ):
        require_phase(SystemPhase.LIVE)

        if not self.approval.is_approved(strategy_meta.strategy_id):
            raise RuntimeError("LIVE approval missing")

        if self.kill_switch.is_killed(
            strategy_id=strategy_meta.strategy_id,
            symbol=symbol,
        ):
            raise RuntimeError("Execution blocked by kill switch")

        order_value = quantity * price
        self.capital_guard.check(strategy_meta.strategy_id, order_value)

        # Actual broker execution happens here (outside scope)
        return {
            "strategy": strategy_meta.strategy_id,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "status": "LIVE_EXECUTED",
        }
