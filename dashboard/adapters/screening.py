from core.dashboard.snapshot import CoreSystemSnapshot
from dashboard.view_models import ScreeningVM


def screening_adapter(snapshot: CoreSystemSnapshot) -> ScreeningVM:
    """
    Phase-9.2 adapter:
    Screening snapshot → ScreeningVM
    """

    if snapshot.screening is None:
        return ScreeningVM(
            available=False,
            type=None,
        )

    return ScreeningVM(
        available=True,
        type=type(snapshot.screening).__name__,
    )
