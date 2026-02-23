from __future__ import annotations

from datetime import datetime

from core.v2.live_bridge.guards.divergence_guard import DivergenceGuard
from core.v2.live_bridge.shadow.drift_snapshot import DriftSnapshot
from core.v2.operator_dashboard.cli import OperatorCLI
from core.v2.operator_dashboard.aggregators import DashboardAggregator
from core.v2.operator_dashboard.actions import OperatorActions
from core.v2.paper_capital.lifecycle import StrategyLifecycle, LifecycleState
from core.v2.live_bridge.approvals.approval_store import ApprovalStore
from core.v2.live_bridge.contracts import LiveGateDecision


def run_drill_divergence_breach(
    *,
    strategy_id: str,
    operator: str,
) -> None:
    """
    Drill 4: Divergence breach triggers automatic deny.
    """

    now = datetime.utcnow()

    # --- System wiring ---
    approval_store = ApprovalStore()
    actions = OperatorActions(approval_store=approval_store)
    aggregator = DashboardAggregator()
    cli = OperatorCLI(
        aggregator=aggregator,
        actions=actions,
        approval_store=approval_store,
    )

    lifecycle = StrategyLifecycle(strategy_id=strategy_id)
    lifecycle.state = LifecycleState.PAPER_ACTIVE

    # --- Issue approval (should not matter) ---
    cli.approve(
        strategy_id=strategy_id,
        operator=operator,
        ttl_minutes=60,
        notes="Drill 4 — divergence breach test",
        now=now,
    )

    # --- Inject divergence ---
    guard = DivergenceGuard(
        max_pnl_diff=10.0,
        max_trade_diff=1,
    )

    snapshot = DriftSnapshot(
        strategy_id=strategy_id,
        paper_pnl=100.0,
        live_pnl=10.0,  # large divergence
        paper_trades=10,
        live_trades=10,
        captured_at=now,
    )

    decision = guard.evaluate(
        snapshot=snapshot,
        now=now,
    )

    assert decision.allowed is False
    assert "pnl_divergence" in decision.reasons

    # --- Operator view reflects denial ---
    status = cli.status(
        lifecycle=lifecycle,
        shadow_pnl=100.0,
        gate_decision=decision,
        now=now,
    )

    assert status["safety"].live_allowed is False
