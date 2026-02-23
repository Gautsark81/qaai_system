# qaai_system/execution/execution_orchestrator.py #
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional
import time
import uuid


@dataclass
class TargetPosition:
    symbol: str
    target_qty: int  # signed
    time_in_force: str = "DAY"


@dataclass
class ExecPlan:
    symbol: str
    side: str  # BUY/SELL
    qty: int
    algo: str  # "MKT-SLICE", "LIMIT-PASSIVE", "VWAP"
    limit_price: Optional[float] = None
    idempotency_key: str = ""


class ExecutionOrchestrator:
    def __init__(self, router, risk, store, clock=time):
        self.router = router
        self.risk = risk
        self.store = store
        self.clock = clock

    def rebalance(
        self, targets: List[TargetPosition], mid_prices: Dict[str, float]
    ) -> Dict:
        """Compute deltas → risk checks → submit → monitor → return summary."""
        plans: List[ExecPlan] = self._make_plans(targets, mid_prices)
        accepted = []
        for p in plans:
            self.risk.pre_trade_check(p, mid_prices.get(p.symbol))
            p.idempotency_key = f"{p.symbol}:{uuid.uuid4()}"
            oid = self.router.submit(p)
            self.store.persist_order_plan(p, oid)
            accepted.append((p, oid))
        # monitor fills and reconcile
        summary = self._monitor_and_reconcile([oid for _, oid in accepted])
        self.risk.post_trade_update(summary)
        return summary

    def _make_plans(self, targets, mids):
        # simple MVP: market slicing with size caps
        plans = []
        for t in targets:
            side = "BUY" if t.target_qty > 0 else "SELL"
            qty = abs(t.target_qty)
            if qty == 0:
                continue
            # TODO: use volatility/ADV to pick algo & slice size
            plans.append(
                ExecPlan(symbol=t.symbol, side=side, qty=qty, algo="MKT-SLICE")
            )
        return plans

    def _monitor_and_reconcile(self, order_ids):
        # poll router for status, compute slippage, realized cost
        # return dict with per-order & aggregate metrics
        return self.router.settle(order_ids)
