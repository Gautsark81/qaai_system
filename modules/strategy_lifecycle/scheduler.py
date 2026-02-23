# modules/strategy_lifecycle/scheduler.py

from typing import Iterable, Iterator

from modules.strategy_lifecycle.store import StrategyLifecycleStore


class StrategyScheduler:
    """
    Phase 9 Strategy Scheduler (PURE).

    Responsibilities:
    - Select runnable strategies
    - NO infra
    - NO job registration
    - NO execution hooks
    - NO side effects
    """

    def __init__(self, store: StrategyLifecycleStore):
        self.store = store

    def select_runnable(
        self,
        strategy_ids: Iterable[str],
    ) -> Iterator[str]:
        """
        Yield strategy_ids that are allowed to run.
        """
        for strategy_id in strategy_ids:
            if self.store.is_active(strategy_id):
                yield strategy_id
