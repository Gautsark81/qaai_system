from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict

from core.strategy_factory.health.reports.strategy_health_aggregator import (
    StrategyHealthAggregator,
)
from core.strategy_factory.health.strategy_health_report import (
    StrategyHealthStatus,
)


class StrategyLifecycleAction(str, Enum):
    PROMOTE = "PROMOTE"
    HOLD = "HOLD"
    WATCH = "WATCH"
    DEMOTE = "DEMOTE"
    SUNSET = "SUNSET"


@dataclass(frozen=True)
class StrategyLifecycleController:
    """
    Advisory-only lifecycle controller.

    Translates health signals into lifecycle actions.
    Never executes, never allocates capital, never overrides governance.
    """

    aggregator: StrategyHealthAggregator

    advisory_only: bool = field(init=False, default=True)
    actions_by_strategy: Dict[str, StrategyLifecycleAction] = field(init=False)

    # ----------------------------
    # Lifecycle
    # ----------------------------

    def __post_init__(self):
        self._derive_actions()

    # ----------------------------
    # Core Logic
    # ----------------------------

    def _derive_actions(self) -> None:
        actions: Dict[str, StrategyLifecycleAction] = {}

        promote_allowed = (
            self.aggregator.promotion_pressure
            and not self.aggregator.demotion_pressure
        )

        for report in self.aggregator.reports:
            status = report.status

            if status == StrategyHealthStatus.HEALTHY:
                if promote_allowed:
                    action = StrategyLifecycleAction.PROMOTE
                else:
                    action = StrategyLifecycleAction.HOLD

            elif status == StrategyHealthStatus.DEGRADED:
                action = StrategyLifecycleAction.WATCH

            elif status == StrategyHealthStatus.DYING:
                action = StrategyLifecycleAction.DEMOTE

            elif status == StrategyHealthStatus.DEAD:
                action = StrategyLifecycleAction.SUNSET

            else:
                raise AssertionError(f"Unhandled strategy status: {status}")

            actions[report.strategy_id] = action

        object.__setattr__(self, "actions_by_strategy", actions)
