# tests/strategies/test_strategy_health_persistence.py

import tempfile
import os

from modules.strategies.health.store import StrategyHealthStore
from modules.strategies.health.types import StrategyState


def test_disabled_strategy_survives_restart():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "health.json")

        store1 = StrategyHealthStore(max_failures=1, persist_path=path)
        store1.record_failure("s1", "boom")

        # simulate restart
        store2 = StrategyHealthStore(max_failures=1, persist_path=path)
        health = store2.get("s1")

        assert health.state == StrategyState.DISABLED
        assert health.failure_count == 1
