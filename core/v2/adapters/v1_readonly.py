from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class V1StrategySnapshot:
    strategy_id: str
    ssr: float
    health: float
    regime_fit: float
    stability: float
    lifecycle_state: str
    capital_approved: bool


class V1ReadonlyAdapter:
    """
    STRICT READ-ONLY bridge to v1 state.

    🚨 RULE:
    - NO mutation
    - NO side effects
    - Any unexpected attribute access = hard failure
    """

    def __init__(self, v1_store: Any):
        self._store = v1_store

    def snapshot_strategy(self, strategy_id: str) -> V1StrategySnapshot:
        raw = self._store.get_strategy_snapshot(strategy_id)

        return V1StrategySnapshot(
            strategy_id=raw["strategy_id"],
            ssr=raw["ssr"],
            health=raw["health"],
            regime_fit=raw["regime_fit"],
            stability=raw["stability"],
            lifecycle_state=raw["lifecycle_state"],
            capital_approved=raw["capital_approved"],
        )
