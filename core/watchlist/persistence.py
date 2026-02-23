from pathlib import Path
import json

from core.watchlist.models import WatchlistEntry, WatchlistSnapshot

WATCHLIST_PATH = Path("watchlist.json")


def save_snapshot(snapshot: WatchlistSnapshot, path: Path | None = None):
    if path is None:
        path = WATCHLIST_PATH

    entries = []
    for e in snapshot.entries:
        if isinstance(e, WatchlistEntry):
            entries.append(
                {
                    "symbol": e.symbol,
                    "rank": e.rank,
                    "confidence": e.confidence,
                    "source": e.source,
                    "reasons": e.reasons,
                }
            )
        else:
            # legacy: raw symbol string
            entries.append(
                {
                    "symbol": str(e),
                    "rank": 0,
                    "confidence": 0.0,
                    "source": "unknown",
                    "reasons": [],
                }
            )

    payload = {
        "created_ts": snapshot.created_ts,
        "source": snapshot.source,
        "version": snapshot.version,
        "entries": entries,
    }

    with Path(path).open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def load_snapshot(path: Path | None = None) -> WatchlistSnapshot:
    if path is None:
        path = WATCHLIST_PATH

    with Path(path).open("r", encoding="utf-8") as f:
        data = json.load(f)

    entries = [
        WatchlistEntry(
            symbol=e["symbol"],
            rank=e.get("rank", 0),
            confidence=e.get("confidence", 0.0),
            source=e.get("source", "screening"),
            reasons=e.get("reasons", []),
        )
        for e in data.get("entries", [])
    ]

    return WatchlistSnapshot(
        entries=entries,
        created_ts=data.get("created_ts", ""),
        source=data.get("source", "screening"),
        version=data.get("version", "v1"),
    )
