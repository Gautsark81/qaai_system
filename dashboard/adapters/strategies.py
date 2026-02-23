from core.dashboard.snapshot import CoreSystemSnapshot
from dashboard.view_models import StrategiesVM


def strategy_adapter(snapshot: CoreSystemSnapshot) -> StrategiesVM:
    """
    Phase-9.2 adapter:
    Strategies snapshot → StrategiesVM
    """

    if snapshot.strategies is None:
        return StrategiesVM(
            available=False,
            type=None,
        )

    return StrategiesVM(
        available=True,
        type=type(snapshot.strategies).__name__,
    )
