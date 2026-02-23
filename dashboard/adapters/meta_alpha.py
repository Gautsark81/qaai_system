from core.dashboard.snapshot import CoreSystemSnapshot
from dashboard.view_models import MetaAlphaVM


def meta_alpha_adapter(snapshot: CoreSystemSnapshot) -> MetaAlphaVM:
    """
    Phase-9.2 adapter:
    Meta-alpha is observational only (no execution authority).
    """

    if snapshot.capital is None:
        return MetaAlphaVM(
            enabled=False,
            total_allocated=0.0,
            allocations=(),
        )

    # No allocation logic yet (future Phase-C)
    return MetaAlphaVM(
        enabled=True,
        total_allocated=0.0,
        allocations=(),
    )
