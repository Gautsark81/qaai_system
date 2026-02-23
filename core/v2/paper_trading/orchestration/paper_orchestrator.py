from __future__ import annotations

from datetime import datetime
from typing import Iterable

from core.v2.paper_trading.contracts import PaperTradeCycle
from core.v2.paper_trading.execution.execution_engine import ExecutionEngine
from core.v2.paper_trading.orders.order import PaperOrderRequest
from core.v2.paper_trading.pnl.ledger import PnLLedger
from core.v2.paper_capital.lifecycle import StrategyLifecycle


class PaperOrchestrator:
    """
    Orchestrates a full paper trading cycle.
    """

    def __init__(
        self,
        *,
        execution_engine: ExecutionEngine,
        pnl_ledger: PnLLedger,
        lifecycle: StrategyLifecycle,
    ):
        self._engine = execution_engine
        self._ledger = pnl_ledger
        self._lifecycle = lifecycle

    def run_cycle(
        self,
        *,
        strategy_id: str,
        promoted: bool,
        symbol: str,
        side: str,
    ) -> PaperTradeCycle:
        started_at = datetime.utcnow()

        orders_created = 0
        fills_created = 0
        pnl_before = sum(e.delta for e in self._ledger.entries())

        if promoted:
            req = PaperOrderRequest(
                strategy_id=strategy_id,
                symbol=symbol,
                side=side,
                quantity=1,
                created_at=started_at,
            )

            fill = self._engine.submit(req)
            self._ledger.record(fill=fill, strategy_id=strategy_id)

            orders_created = 1
            fills_created = 1

            # Update lifecycle based on outcome
            outcome = fill.delta > 0 if hasattr(fill, "delta") else True
            self._lifecycle.record_outcomes([outcome])

        pnl_after = sum(e.delta for e in self._ledger.entries())
        ended_at = datetime.utcnow()

        return PaperTradeCycle(
            cycle_id=f"cycle-{started_at.timestamp()}",
            started_at=started_at,
            ended_at=ended_at,
            orders_created=orders_created,
            fills_created=fills_created,
            pnl_delta=pnl_after - pnl_before,
        )
