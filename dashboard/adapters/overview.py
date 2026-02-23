from core.dashboard.snapshot import CoreSystemSnapshot
from dashboard.view_models import OverviewVM


def overview_adapter(snapshot: CoreSystemSnapshot) -> OverviewVM:
    """
    Phase-9.2 adapter:
    CoreSystemSnapshot → OverviewVM
    """

    return OverviewVM(
        timestamp=snapshot.timestamp,
        alert_count=len(snapshot.alerts),
        has_screening=snapshot.screening is not None,
        has_watchlist=snapshot.watchlist is not None,
        has_strategies=snapshot.strategies is not None,
        has_capital=snapshot.capital is not None,
    )
