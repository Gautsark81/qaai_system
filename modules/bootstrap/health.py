# modules/bootstrap/health.py

from modules.strategies.health.store import StrategyHealthStore


def build_health_store() -> StrategyHealthStore:
    return StrategyHealthStore(
        max_failures=3,
        persist_path="state/strategy_health.json",
    )
