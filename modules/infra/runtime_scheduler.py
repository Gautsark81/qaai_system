# modules/infra/runtime_scheduler.py

import time
from typing import Iterable, Callable

from modules.strategy_lifecycle.scheduler import StrategyScheduler
from modules.execution.execution_gate import ExecutionGate


class RuntimeScheduler:
    """
    Phase 10 Runtime Scheduler (INFRA).

    Responsibilities:
    - Own wall-clock timing
    - Periodically trigger strategy evaluation
    - Delegate selection to Phase-9 scheduler
    - Delegate execution to Phase-10 gate

    Explicitly allowed:
    - time.sleep
    - loops
    - clocks

    Explicitly forbidden:
    - strategy logic
    - lifecycle mutation
    - execution logic
    """

    def __init__(
        self,
        *,
        scheduler: StrategyScheduler,
        execution_gate: ExecutionGate,
        tick_seconds: float,
        strategy_ids_provider: Callable[[], Iterable[str]],
        on_tick: Callable[[str], None],
    ):
        self._scheduler = scheduler
        self._execution_gate = execution_gate
        self._tick_seconds = tick_seconds
        self._strategy_ids_provider = strategy_ids_provider
        self._on_tick = on_tick
        self._running = False
        self._running = True

    def start(self, *, max_ticks: int | None = None) -> None:
        """
        Start the runtime loop.

        Args:
            max_ticks: optional bound for testability
        """
        # Respect prior stop()
        if not self._running:
            return

        tick_count = 0

        while self._running:
            tick_count += 1

            # --- Select runnable strategies (PURE)
            runnable = self._scheduler.select_runnable(
                self._strategy_ids_provider()
            )

            # --- Trigger evaluation hooks
            for strategy_id in runnable:
                self._on_tick(strategy_id)

            # --- Exit for bounded runs (tests)
            if max_ticks is not None and tick_count >= max_ticks:
                break

            time.sleep(self._tick_seconds)


    def stop(self) -> None:
        self._running = False
