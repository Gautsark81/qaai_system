from core.operator_dashboard.adapters.strategy_lifecycle_adapter import (
    load_strategy_lifecycle_views,
)
from core.operator_dashboard.adapters.system_health_adapter import (
    load_system_health,
)


class OperatorDashboardBackend:
    """
    Single entry point for dashboard UI.
    """

    @staticmethod
    def get_system_health():
        return load_system_health()

    @staticmethod
    def get_strategy_lifecycle():
        return load_strategy_lifecycle_views()
