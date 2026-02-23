from modules.operator_dashboard.registry import DashboardSnapshotRegistry
from modules.operator_dashboard.contracts.dashboard_snapshot import DashboardSnapshot


class DashboardService:
    """
    Facade service.

    Does NOT assemble snapshots.
    Delegates to SnapshotRegistry to ensure determinism.
    """

    def __init__(self, registry, confidence_engine=None):
        self._snapshot_registry = DashboardSnapshotRegistry(
            strategy_registry=registry,
            confidence_engine=confidence_engine,
        )

    def build_snapshot(self) -> DashboardSnapshot:
        return self._snapshot_registry.build()
