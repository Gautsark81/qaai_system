# tests/strategies/test_health_corruption_safe.py

import tempfile
import os

from modules.strategies.health.store import StrategyHealthStore
from modules.strategies.health.types import StrategyState


def test_corrupt_health_file_falls_back_safely():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "health.json")

        with open(path, "w", encoding="utf-8") as f:
            f.write("not valid json")

        store = StrategyHealthStore(max_failures=1, persist_path=path)

        health = store.get("any")
        assert health.state == StrategyState.ACTIVE
