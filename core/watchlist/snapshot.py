from typing import List
from datetime import datetime
import pandas as pd

from core.watchlist.models import WatchlistEntry, WatchlistSnapshot


def build_snapshot(
    entries: List[WatchlistEntry],
    source: str = "screening",
) -> WatchlistSnapshot:
    return WatchlistSnapshot(
        entries=entries,
        created_ts=datetime.utcnow().isoformat(),
        source=source,
    )


def _to_frame(snapshot: WatchlistSnapshot) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "symbol": e.symbol,
                "rank": e.rank,
                "confidence": e.confidence,
                "source": e.source,
            }
            for e in snapshot.entries
        ]
    )


@property
def _iloc(self):
    return _to_frame(self).iloc


# Legacy test compatibility
WatchlistSnapshot.iloc = _iloc
