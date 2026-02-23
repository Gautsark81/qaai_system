from datetime import datetime
from unittest.mock import Mock

from modules.infra.runtime_scheduler import RuntimeScheduler
from modules.execution.execution_gate import ExecutionGate
from modules.strategy_lifecycle.scheduler import StrategyScheduler
from modules.strategy_lifecycle.store import StrategyLifecycleStore
from modules.strategy_lifecycle.states import StrategyState
from modules.strategies.intent import StrategyIntent


def test_end_to_end_tick_selects_gates_and_executes_once():
    """
    End-to-end wiring test:
    clock -> selector -> lifecycle gate -> execution submit
    """

    # ---- Phase 9: lifecycle store (pure)
    lifecycle_store = StrategyLifecycleStore()
    lifecycle_store.set_state("s_active", StrategyState.ACTIVE)
    lifecycle_store.set_state("s_disabled", StrategyState.DISABLED)

    selector = StrategyScheduler(lifecycle_store)

    # ---- Phase 10.1: execution gate
    execution_orchestrator = Mock()

    lifecycle_orchestrator = Mock()
    lifecycle_orchestrator.can_execute.side_effect = (
        lambda sid: lifecycle_store.is_active(sid)
    )

    gate = ExecutionGate(
        lifecycle_orchestrator=lifecycle_orchestrator,
        execution_orchestrator=execution_orchestrator,
    )

    # ---- intent factory (locked Phase-9 contract)
    def make_intent(strategy_id: str):
        return StrategyIntent(
            strategy_id=strategy_id,
            side="BUY",
            symbol="TEST",
            confidence=0.9,
            features_used=["f1"],
            timestamp=datetime.utcnow(),
        )

    # ---- evaluation hook (called by RuntimeScheduler)
    def on_tick(strategy_id: str):
        intent = make_intent(strategy_id)
        gate.handle_intent(
            strategy_id=strategy_id,
            intent=intent,
            order_id=f"order-{strategy_id}",
            order_payload={"symbol": "TEST"},
        )

    # ---- Phase 10.2: runtime scheduler (infra)
    runtime = RuntimeScheduler(
        scheduler=selector,
        execution_gate=gate,
        tick_seconds=0,
        strategy_ids_provider=lambda: ["s_active", "s_disabled"],
        on_tick=on_tick,
    )

    # ---- run exactly one tick
    runtime.start(max_ticks=1)

    # ---- assertions
    execution_orchestrator.submit_order.assert_called_once_with(
        order_id="order-s_active",
        order_payload={"symbol": "TEST"},
    )
