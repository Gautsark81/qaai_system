# core/paper/paper_executor.py

from core.paper.paper_ledger import PaperLedger
from core.runtime.deterministic_context import DeterministicContext

from core.safety.kill_switch import KillSwitch
from core.safety.scopes import KillScope


class PaperExecutor:
    """
    Deterministic paper trade executor with hard safety enforcement.
    """

    def __init__(
        self,
        *,
        deterministic: bool = True,
        kill_switch: KillSwitch | None = None,
    ):
        self.deterministic = deterministic
        self.ledger = PaperLedger()
        self.kill_switch = kill_switch or KillSwitch()

    def execute(self, strategy_id, symbol, side, qty, price):
        # 🔒 STEP-9.1 — GLOBAL KILL
        self.kill_switch.assert_can_trade()

        # 🔒 STEP-9.2 — STRATEGY-LEVEL KILL
        if self.kill_switch.is_tripped(KillScope.STRATEGY, key=strategy_id):
            reason = self.kill_switch.reason(KillScope.STRATEGY, key=strategy_id)
            raise RuntimeError(
                f"Trading halted for strategy {strategy_id}: {reason}"
            )

        # 🔒 STEP-9.4 — BAD DATA HARD HALT
        if price is None or price <= 0:
            raise RuntimeError("Invalid market data: price")

        if qty is None or qty <= 0:
            raise RuntimeError("Invalid market data: quantity")

        if side not in ("BUY", "SELL"):
            raise RuntimeError("Invalid market data: side")

        timestamp = (
            DeterministicContext.now()
            if self.deterministic
            else None
        )

        trade = {
            "strategy_id": strategy_id,
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "price": price,
            "timestamp": timestamp.isoformat() if timestamp else None,
        }

        self.ledger.record(trade)
        return trade
