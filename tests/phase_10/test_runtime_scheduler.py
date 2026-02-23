from unittest.mock import Mock

from modules.infra.runtime_scheduler import RuntimeScheduler


def test_scheduler_triggers_only_active_strategies():
    # --- mocks
    scheduler = Mock()
    scheduler.select_runnable.return_value = ["s1", "s3"]

    execution_gate = Mock()

    strategy_ids_provider = Mock(return_value=["s1", "s2", "s3"])

    on_tick = Mock()

    runtime = RuntimeScheduler(
        scheduler=scheduler,
        execution_gate=execution_gate,
        tick_seconds=0,
        strategy_ids_provider=strategy_ids_provider,
        on_tick=on_tick,
    )

    runtime.start(max_ticks=1)

    # on_tick called only for runnable strategies
    on_tick.assert_any_call("s1")
    on_tick.assert_any_call("s3")
    assert on_tick.call_count == 2


def test_scheduler_respects_max_ticks():
    scheduler = Mock()
    scheduler.select_runnable.return_value = []

    execution_gate = Mock()
    strategy_ids_provider = Mock(return_value=[])

    on_tick = Mock()

    runtime = RuntimeScheduler(
        scheduler=scheduler,
        execution_gate=execution_gate,
        tick_seconds=0,
        strategy_ids_provider=strategy_ids_provider,
        on_tick=on_tick,
    )

    runtime.start(max_ticks=3)

    assert scheduler.select_runnable.call_count == 3


def test_scheduler_can_be_stopped():
    scheduler = Mock()
    scheduler.select_runnable.return_value = []

    execution_gate = Mock()
    strategy_ids_provider = Mock(return_value=[])

    on_tick = Mock()

    runtime = RuntimeScheduler(
        scheduler=scheduler,
        execution_gate=execution_gate,
        tick_seconds=0,
        strategy_ids_provider=strategy_ids_provider,
        on_tick=on_tick,
    )

    runtime.stop()
    runtime.start(max_ticks=1)

    # stop before start prevents execution
    scheduler.select_runnable.assert_not_called()
