from datetime import datetime
import inspect
from typing import Optional

from core.strategy_factory.registry import StrategyRegistry
from core.phase_b.confidence import ConfidenceEngine

from modules.operator_dashboard.contracts.dashboard_snapshot import (
    DashboardSnapshot,
)
from modules.operator_dashboard.adapters.oversight_adapter import (
    get_oversight_event_snapshots,
)
from modules.operator_dashboard.snapshot import (
    get_system_health_snapshot,
    get_capital_snapshot,
    get_strategy_snapshots,
    get_alerts_snapshot,
    get_explainability_snapshot,
)


class DashboardSnapshotRegistry:
    """
    Read-only dashboard snapshot builder.

    HARD RULES:
    - No mutation
    - No business logic
    - Phase-F contract compliant
    """

    def __init__(
        self,
        registry: Optional[StrategyRegistry] = None,
        confidence_engine: Optional[ConfidenceEngine] = None,
        *,
        strategy_registry: Optional[StrategyRegistry] = None,
    ):
        # -------------------------------------------------------------
        # Accept BOTH registry styles (tests + service depend on this)
        # -------------------------------------------------------------
        if strategy_registry is not None:
            self._strategy_registry = strategy_registry
        elif registry is not None:
            self._strategy_registry = registry
        else:
            self._strategy_registry = StrategyRegistry.global_instance()

        self._confidence_engine = confidence_engine

        # -------------------------------------------------------------
        # Snapshot constructor introspection (future-proof)
        # -------------------------------------------------------------
        self._snapshot_fields = set(
            inspect.signature(DashboardSnapshot).parameters.keys()
        )

    def build(self) -> DashboardSnapshot:
        now = datetime.utcnow()

        # -------------------------------------------------------------
        # Core read-only surfaces
        # -------------------------------------------------------------
        strategies = get_strategy_snapshots(
            registry=self._strategy_registry,
            confidence_engine=self._confidence_engine,
        )

        payload = {
            "timestamp": now,
            "system": get_system_health_snapshot(),
            "strategies": strategies,            # ✅ KEEP AS DICT
            "alerts": tuple(get_alerts_snapshot()),
            "capital": get_capital_snapshot(),
            "oversight_events": tuple(
                get_oversight_event_snapshots()
            ),
        }

        # -------------------------------------------------------------
        # Optional / future-safe surfaces
        # -------------------------------------------------------------
        if "explainability" in self._snapshot_fields:
            payload["explainability"] = get_explainability_snapshot()

        if "regime" in self._snapshot_fields:
            try:
                from modules.operator_dashboard.snapshot import (
                    get_regime_snapshot,
                )
                payload["regime"] = get_regime_snapshot()
            except Exception:
                pass

        return DashboardSnapshot(**payload)
