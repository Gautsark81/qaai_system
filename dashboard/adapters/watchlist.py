from core.dashboard.snapshot import CoreSystemSnapshot
from dashboard.view_models import WatchlistVM


def watchlist_adapter(snapshot: CoreSystemSnapshot) -> WatchlistVM:
    """
    Phase-9.2 adapter:
    Watchlist snapshot → WatchlistVM
    """

    if snapshot.watchlist is None:
        return WatchlistVM(
            available=False,
            count=None,
            type=None,
        )

    count = (
        len(snapshot.watchlist)
        if hasattr(snapshot.watchlist, "__len__")
        else None
    )

    return WatchlistVM(
        available=True,
        count=count,
        type=type(snapshot.watchlist).__name__,
    )
